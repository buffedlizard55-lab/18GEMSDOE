import { fromBlob, writeArrayBuffer } from 'geotiff';

function fail(message) {
  throw new Error(message);
}

function isNoData(value, noData) {
  if (noData === null || noData === undefined) return false;
  if (Number.isNaN(noData)) return Number.isNaN(value);
  return value === noData;
}

function gridInfo(image) {
  const geoKeys = image.getGeoKeys() || {};
  const resolution = image.getResolution();
  const origin = image.getOrigin();
  const transformation = image.getFileDirectory().getValue('ModelTransformation');
  const rotated = transformation && (Math.abs(transformation[1]) > 1e-8 || Math.abs(transformation[4]) > 1e-8);
  return {
    width: image.getWidth(),
    height: image.getHeight(),
    epsg: geoKeys.ProjectedCSTypeGeoKey || null,
    resolution,
    origin,
    rotated: Boolean(rotated),
    geoKeys,
  };
}

function sameGrid(reference, candidate, label) {
  const a = gridInfo(reference);
  const b = gridInfo(candidate);
  if (a.width !== b.width || a.height !== b.height) fail(`${label}: raster dimensions differ from the template.`);
  if (a.epsg !== 32611 || b.epsg !== 32611) fail(`${label}: both rasters must use projected EPSG:32611.`);
  if (a.rotated || b.rotated) fail(`${label}: the official grid must be unrotated.`);
  for (let i = 0; i < 2; i += 1) {
    if (Math.abs(a.resolution[i] - b.resolution[i]) > 1e-8) fail(`${label}: pixel resolution differs from the template.`);
    if (Math.abs(a.origin[i] - b.origin[i]) > 1e-6) fail(`${label}: grid origin differs from the template.`);
  }
  if (Math.abs(Math.abs(a.resolution[0]) - 100) > 1e-8 || Math.abs(Math.abs(a.resolution[1]) - 100) > 1e-8) {
    fail(`${label}: the official grid must be 100 m.`);
  }
}

function validateEvidence(evidence, candidateId) {
  if (!evidence || typeof evidence !== 'object') fail('Holdout evidence JSON is missing or invalid.');
  if (evidence.schema_version !== 1) fail('Unsupported holdout evidence schema.');
  if (evidence.candidate_id !== candidateId) fail('Evidence candidate ID does not match.');
  if (evidence.pre_registered !== true || evidence.holdout_locked_before_tuning !== true) {
    fail('A preregistered candidate and holdout locked before tuning are required.');
  }
  if (evidence.baseline_independently_reproduced !== true || evidence.baseline?.status !== 'INDEPENDENTLY_REPRODUCED') {
    fail('The holdout comparator must be independently reproduced.');
  }
  if (evidence.negative_controls_pass !== true || evidence.content_unique !== true) {
    fail('Negative controls and the uniqueness check must pass.');
  }
  if (evidence.gate_status !== 'PASS' || !evidence.holdout_id) fail('The spatial holdout release gate is not marked PASS.');
  for (const key of ['holdout_manifest_sha256', 'input_manifest_sha256']) {
    if (!/^[0-9a-f]{64}$/i.test(evidence[key] || '')) fail(`${key} must be a 64-character SHA-256.`);
  }
  if (!evidence.preregistration_commit) fail('The preregistration commit is required.');

  const metricDeltas = {};
  for (const metric of ['dense', 'sparse']) {
    const base = evidence.baseline[`${metric}_fold_dti`];
    const candidate = evidence.candidate?.[`${metric}_fold_dti`];
    if (!Array.isArray(base) || !Array.isArray(candidate) || base.length !== 4 || candidate.length !== 4) {
      fail(`Exactly four baseline and candidate ${metric} fold scores are required.`);
    }
    if (![...base, ...candidate].every((n) => typeof n === 'number' && Number.isFinite(n))) fail(`${metric} fold scores must be finite numbers.`);
    metricDeltas[metric] = candidate.map((score, index) => score - base[index]);
    const mean = (arr) => arr.reduce((sum, n) => sum + n, 0) / arr.length;
    if (mean(candidate) <= mean(base)) fail(`Mean ${metric} DTI does not exceed the reproduced comparator.`);
    if (Math.min(...metricDeltas[metric]) < -0.01) fail(`A ${metric} fold loses more than 0.01 DTI.`);
  }
  if (metricDeltas.sparse.filter((delta) => delta > 0).length < 3) fail('Sparse DTI must improve in at least three of four folds.');
  const bounds = evidence.paired_block_bootstrap_95pct_lower_bound;
  if (!bounds || !['dense', 'sparse'].every((metric) => typeof bounds[metric] === 'number' && Number.isFinite(bounds[metric]) && bounds[metric] > 0)) {
    fail('Positive paired block-bootstrap 95% lower bounds are required for both metrics.');
  }
  return true;
}

function buildWriterMetadata(templateImage) {
  const directory = templateImage.getFileDirectory();
  const geoKeys = templateImage.getGeoKeys() || {};
  const metadata = {
    width: templateImage.getWidth(),
    height: templateImage.getHeight(),
    BitsPerSample: [32],
    SampleFormat: [3],
    SamplesPerPixel: [1],
    PhotometricInterpretation: 1,
    Compression: 1,
    PlanarConfiguration: 1,
    GDAL_NODATA: 'nan',
  };
  for (const key of ['ModelPixelScale', 'ModelTiepoint', 'ModelTransformation']) {
    const value = directory.getValue(key);
    if (value) metadata[key] = Array.from(value);
  }
  for (const [key, value] of Object.entries(geoKeys)) {
    if (typeof value === 'number' || typeof value === 'string') metadata[key] = value;
  }
  if (!metadata.ProjectedCSTypeGeoKey) fail('Template is missing ProjectedCSTypeGeoKey.');
  return metadata;
}

async function sha256Hex(arrayBuffer) {
  if (!globalThis.crypto?.subtle) fail('This browser does not support Web Crypto SHA-256. Use the Python packager instead.');
  const digest = await globalThis.crypto.subtle.digest('SHA-256', arrayBuffer);
  return Array.from(new Uint8Array(digest), (value) => value.toString(16).padStart(2, '0')).join('');
}

function safeSlug(value) {
  const slug = String(value).trim().toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 48);
  if (!slug) fail('Candidate ID must contain letters or digits.');
  return slug;
}

/**
 * Read a prediction and the official sample locally, verify the locked evidence,
 * write a float32 GeoTIFF on the exact template grid, re-read it, and return a Blob.
 * Nothing is uploaded or sent to a service.
 */
export async function buildSubmission({ predictionFile, templateFile, evidenceFile, footprintFile = null, candidateId, now = new Date() }) {
  if (!predictionFile || !templateFile || !evidenceFile) fail('Prediction, official template, and passing holdout evidence files are required.');
  if (!candidateId) fail('Candidate ID is required.');

  const evidence = JSON.parse(await evidenceFile.text());
  validateEvidence(evidence, candidateId);
  const [predictionTiff, templateTiff] = await Promise.all([fromBlob(predictionFile), fromBlob(templateFile)]);
  const prediction = await predictionTiff.getImage();
  const template = await templateTiff.getImage();
  if (prediction.getSamplesPerPixel() !== 1 || template.getSamplesPerPixel() !== 1) fail('Prediction and template must each have one band.');
  sameGrid(template, prediction, 'Prediction');

  const [predictionData, templateData] = await Promise.all([
    prediction.readRasters({ samples: [0], interleave: true }),
    template.readRasters({ samples: [0], interleave: true }),
  ]);
  const width = template.getWidth();
  const height = template.getHeight();
  const n = width * height;
  if (predictionData.length !== n || templateData.length !== n) fail('Raster data length does not match the template grid.');

  let footprintData = null;
  let footprintImage = null;
  let footprintNoData = null;
  if (footprintFile) {
    const footprintTiff = await fromBlob(footprintFile);
    footprintImage = await footprintTiff.getImage();
    if (footprintImage.getSamplesPerPixel() !== 1) fail('Footprint mask must have one band.');
    sameGrid(template, footprintImage, 'Footprint mask');
    footprintData = await footprintImage.readRasters({ samples: [0], interleave: true });
    footprintNoData = footprintImage.getGDALNoData();
  }

  const templateNoData = template.getGDALNoData();
  if (!footprintFile && (templateNoData === null || templateNoData === undefined)) {
    fail('Template has no readable nodata value; provide an explicit scored-footprint mask.');
  }
  const predictionNoData = prediction.getGDALNoData();
  const values = new Float32Array(n);
  let validPixels = 0;
  let minimum = Infinity;
  let maximum = -Infinity;
  for (let i = 0; i < n; i += 1) {
    const templateValue = templateData[i];
    const inside = footprintData
      ? !isNoData(footprintData[i], footprintNoData) && Number.isFinite(footprintData[i]) && footprintData[i] !== 0
      : !isNoData(templateValue, templateNoData) && Number.isFinite(templateValue);
    if (!inside) {
      values[i] = Number.NaN;
      continue;
    }
    const value = predictionData[i];
    if (isNoData(value, predictionNoData) || !Number.isFinite(value)) fail(`Prediction has missing/non-finite data inside the valid footprint at pixel ${i}.`);
    if (value < 0 || value > 1) fail(`Prediction value ${value} at pixel ${i} is outside [0,1]. Nothing was clipped or rescaled.`);
    const f32 = Math.fround(value);
    if (!Number.isFinite(f32) || f32 < 0 || f32 > 1) fail(`float32 conversion would create an invalid value at pixel ${i}.`);
    values[i] = f32;
    validPixels += 1;
    minimum = Math.min(minimum, f32);
    maximum = Math.max(maximum, f32);
  }
  if (!validPixels) fail('Valid footprint is empty.');

  const outputBuffer = writeArrayBuffer(values, buildWriterMetadata(template));
  const outputBlob = new Blob([outputBuffer], { type: 'image/tiff' });
  const outputTiff = await fromBlob(outputBlob);
  const outputImage = await outputTiff.getImage();
  sameGrid(template, outputImage, 'Generated output');
  if (outputImage.getSamplesPerPixel() !== 1 || outputImage.getBitsPerSample(0) !== 32 || outputImage.getSampleFormat(0) !== 3) {
    fail('Generated output did not round-trip as one-band float32.');
  }
  const reread = await outputImage.readRasters({ samples: [0], interleave: true });
  if (reread.length !== n) fail('Generated output has the wrong pixel count.');
  for (let i = 0; i < n; i += 1) {
    if (Number.isNaN(values[i])) {
      if (!Number.isNaN(reread[i])) fail(`Generated output changed outside-footprint pixel ${i}.`);
    } else if (reread[i] !== values[i]) {
      fail(`Generated output pixel ${i} did not round-trip exactly.`);
    }
  }

  const sha = await sha256Hex(outputBuffer);
  const pixelBytes = values.buffer.slice(values.byteOffset, values.byteOffset + values.byteLength);
  const pixelSha = await sha256Hex(pixelBytes);
  const instant = now.toISOString().replace(/[-:]/g, '').replace(/\.(\d{3})Z$/, '$1Z');
  const nonceBytes = new Uint8Array(4);
  globalThis.crypto.getRandomValues(nonceBytes);
  const nonce = Array.from(nonceBytes, (value) => value.toString(16).padStart(2, '0')).join('');
  const filename = `gems18-${safeSlug(candidateId)}-${instant}-${sha.slice(0, 8)}-${nonce}.tif`;
  const note = `18GEMSDOE ${candidateId} | holdout evidence ${evidence.holdout_id} | release gate PASS | SHA-256 ${sha.slice(0, 12)}`;
  return {
    blob: outputBlob,
    filename,
    sha256: sha,
    pixelSha256: pixelSha,
    note,
    report: {
      valid: true,
      width,
      height,
      epsg: 32611,
      resolution: [100, -100],
      validPixels,
      min: minimum,
      max: maximum,
      outputBytes: outputBuffer.byteLength,
      exactRoundTrip: true,
      holdoutId: evidence.holdout_id,
    },
  };
}

export { validateEvidence };
