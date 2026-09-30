import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import { fromBlob, writeArrayBuffer } from 'geotiff';
import { buildSubmission } from '../web/submission-builder.js';

globalThis.crypto ??= webcrypto;
globalThis.FileReader ??= class NodeFileReader {
  readAsArrayBuffer(blob) {
    blob.arrayBuffer().then((buffer) => {
      this.result = buffer;
      this.onload?.();
    }).catch((error) => this.onerror?.(error));
  }
  abort() {
    this.onabort?.();
  }
};

function geotiff(values, width, height, nodata = 'nan') {
  const metadata = {
    width,
    height,
    BitsPerSample: [32],
    SampleFormat: [3],
    SamplesPerPixel: [1],
    PhotometricInterpretation: 1,
    Compression: 1,
    PlanarConfiguration: 1,
    ModelPixelScale: [100, 100, 0],
    ModelTiepoint: [0, 0, 0, 500000, 4400000, 0],
    GTModelTypeGeoKey: 1,
    GTRasterTypeGeoKey: 1,
    ProjectedCSTypeGeoKey: 32611,
  };
  if (nodata !== null) metadata.GDAL_NODATA = nodata;
  const buffer = writeArrayBuffer(values, metadata);
  return new Blob([buffer], { type: 'image/tiff' });
}

const size = 20;
const templateValues = new Float32Array(size).fill(0);
templateValues[size - 1] = Number.NaN;
const predictionValues = new Float32Array(size).fill(0.375);
predictionValues[size - 1] = Number.NaN;
const template = geotiff(templateValues, 5, 4);
const prediction = geotiff(predictionValues, 5, 4);
const evidence = {
  schema_version: 1,
  candidate_id: 'H18-N1',
  pre_registered: true,
  holdout_locked_before_tuning: true,
  baseline_independently_reproduced: true,
  negative_controls_pass: true,
  content_unique: true,
  holdout_id: 'sealed-test',
  holdout_manifest_sha256: 'a'.repeat(64),
  input_manifest_sha256: 'b'.repeat(64),
  preregistration_commit: 'abcdef0',
  gate_status: 'PASS',
  baseline: {
    status: 'INDEPENDENTLY_REPRODUCED',
    dense_fold_dti: [0.2, 0.21, 0.22, 0.23],
    sparse_fold_dti: [0.08, 0.09, 0.1, 0.11],
  },
  candidate: {
    dense_fold_dti: [0.205, 0.215, 0.225, 0.235],
    sparse_fold_dti: [0.09, 0.1, 0.105, 0.12],
  },
  paired_block_bootstrap_95pct_lower_bound: { dense: 0.001, sparse: 0.002 },
};

const result = await buildSubmission({
  predictionFile: prediction,
  templateFile: template,
  evidenceFile: new Blob([JSON.stringify(evidence)], { type: 'application/json' }),
  candidateId: 'H18-N1',
  now: new Date('2026-09-30T12:34:56.000Z'),
});
assert.equal(result.report.valid, true);
assert.equal(result.report.validPixels, 19);
assert.equal(result.report.exactRoundTrip, true);
assert.equal(result.report.min, 0.375);
assert.equal(result.report.max, 0.375);
assert.match(result.filename, /^gems18-h18-n1-/);
assert.match(result.filename, /-[0-9a-f]{8}-[0-9a-f]{8}\.tif$/);
assert.match(result.note, /sealed-test/);
const retryResult = await buildSubmission({
  predictionFile: prediction,
  templateFile: template,
  evidenceFile: new Blob([JSON.stringify(evidence)], { type: 'application/json' }),
  candidateId: 'H18-N1',
  now: new Date('2026-09-30T12:34:56.000Z'),
});
assert.notEqual(retryResult.filename, result.filename);

const reopened = await fromBlob(result.blob);
const image = await reopened.getImage();
assert.equal(image.getWidth(), 5);
assert.equal(image.getHeight(), 4);
assert.equal(image.getGeoKeys().ProjectedCSTypeGeoKey, 32611);
assert.equal(image.getBitsPerSample(0), 32);
assert.equal(image.getSampleFormat(0), 3);

const unlockedEvidence = { ...evidence, holdout_locked_before_tuning: false };
await assert.rejects(
  buildSubmission({ predictionFile: prediction, templateFile: template, evidenceFile: new Blob([JSON.stringify(unlockedEvidence)]), candidateId: 'H18-N1' }),
  /locked before tuning/,
);
const invalidPredictions = new Float32Array(size).fill(0.25);
invalidPredictions[0] = 1.01;
await assert.rejects(
  buildSubmission({ predictionFile: geotiff(invalidPredictions, 5, 4), templateFile: template, evidenceFile: new Blob([JSON.stringify(evidence)]), candidateId: 'H18-N1' }),
  /outside \[0,1\]/,
);

const noDataTemplate = geotiff(new Float32Array(size).fill(0), 5, 4, null);
const maskValues = new Float32Array(size).fill(0);
maskValues[0] = 1;
maskValues[1] = 1;
const explicitMask = geotiff(maskValues, 5, 4, null);
const maskedResult = await buildSubmission({
  predictionFile: geotiff(new Float32Array(size).fill(0.5), 5, 4),
  templateFile: noDataTemplate,
  evidenceFile: new Blob([JSON.stringify(evidence)]),
  footprintFile: explicitMask,
  candidateId: 'H18-N1',
});
assert.equal(maskedResult.report.validPixels, 2);
const maskedTiff = await fromBlob(maskedResult.blob);
const maskedImage = await maskedTiff.getImage();
const maskedOutput = await maskedImage.readRasters({ samples: [0], interleave: true });
assert.ok(Number.isNaN(maskedOutput[2]));
console.log('browser GeoTIFF smoke tests PASS');
