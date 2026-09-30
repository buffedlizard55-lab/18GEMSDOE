(() => {
  'use strict';

  const form = document.getElementById('builder-form');
  if (!form) return;

  const button = document.getElementById('build-button');
  const resultBox = document.getElementById('builder-result');
  const downloads = document.getElementById('builder-downloads');
  const fileInputs = {
    prediction: document.getElementById('prediction-file'),
    template: document.getElementById('template-file'),
    evidence: document.getElementById('evidence-file'),
  };
  const urls = [];

  function clearOldDownloads() {
    for (const url of urls.splice(0)) URL.revokeObjectURL(url);
    downloads.hidden = true;
  }

  function addDownload(anchorId, blob, filename) {
    const url = URL.createObjectURL(blob);
    urls.push(url);
    const anchor = document.getElementById(anchorId);
    anchor.href = url;
    anchor.download = filename;
    anchor.textContent = `Download ${filename}`;
  }

  form.addEventListener('input', () => {
    const ready = Object.values(fileInputs).every((input) => input.files?.length) && document.getElementById('candidate-id').value.trim();
    button.disabled = !ready;
  });
  button.disabled = true;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearOldDownloads();
    resultBox.className = 'builder-result';
    resultBox.textContent = 'Reading local files, checking evidence, and validating the TIFF grid…';
    button.disabled = true;

    try {
      const predictionFile = fileInputs.prediction.files[0];
      const templateFile = fileInputs.template.files[0];
      const evidenceFile = fileInputs.evidence.files[0];
      const footprintFile = document.getElementById('footprint-file').files[0] || null;
      const candidateId = document.getElementById('candidate-id').value.trim();
      const packageResult = await window.GemsSubmissionBuilder.buildSubmission({
        predictionFile,
        templateFile,
        evidenceFile,
        footprintFile,
        candidateId,
      });

      const manifest = {
        candidate_id: candidateId,
        file: packageResult.filename,
        sha256: packageResult.sha256,
        pixel_sha256: packageResult.pixelSha256,
        note: packageResult.note,
        report: packageResult.report,
        created_utc: new Date().toISOString(),
        source_note: 'Locally packaged user-supplied prediction raster; no file upload occurred.',
      };
      const noteBlob = new Blob([`${packageResult.note}\n`], { type: 'text/plain;charset=utf-8' });
      const manifestBlob = new Blob([`${JSON.stringify(manifest, null, 2)}\n`], { type: 'application/json;charset=utf-8' });
      addDownload('download-tiff', packageResult.blob, packageResult.filename);
      addDownload('download-note', noteBlob, packageResult.filename.replace(/\.tif$/i, '.note.txt'));
      addDownload('download-manifest', manifestBlob, packageResult.filename.replace(/\.tif$/i, '.json'));

      resultBox.className = 'builder-result success';
      resultBox.textContent = `Format check PASS · holdout ID ${packageResult.report.holdoutId} · ${packageResult.report.validPixels.toLocaleString()} valid pixels · range ${packageResult.report.min}–${packageResult.report.max} · SHA-256 ${packageResult.sha256}`;
      downloads.hidden = false;
    } catch (error) {
      resultBox.className = 'builder-result error';
      resultBox.textContent = `BLOCKED: ${error instanceof Error ? error.message : String(error)}`;
    } finally {
      const ready = Object.values(fileInputs).every((input) => input.files?.length) && document.getElementById('candidate-id').value.trim();
      button.disabled = !ready;
    }
  });
})();
