# Third-party notices — browser GeoTIFF builder

The static browser builder bundles [`geotiff`](https://github.com/geotiffjs/geotiff.js), version 3.0.5 (MIT), and its production dependencies listed below. The bundled library is used to read a user-selected local GeoTIFF and write a browser-local output. The UI passes `File`/`Blob` objects and does not upload raster data. Python/rasterio remains the independent format check.

| Package | Version | License | Upstream |
|---|---:|---|---|
| geotiff | 3.0.5 | MIT | [geotiff.js](https://github.com/geotiffjs/geotiff.js) |
| @petamoriken/float16 | 3.9.3 | MIT | [float16](https://github.com/petamoriken/float16) |
| lerc | 3.0.0 | Apache-2.0 | [LERC](https://github.com/Esri/lerc) |
| pako | 2.2.0 | MIT AND Zlib | [pako](https://github.com/nodeca/pako) |
| parse-headers | 2.0.6 | MIT | [parse-headers](https://github.com/kesla/parse-headers) |
| quick-lru | 6.1.2 | MIT | [quick-lru](https://github.com/sindresorhus/quick-lru) |
| web-worker | 1.5.0 | Apache-2.0 | [web-worker](https://github.com/developit/web-worker) |
| xml-utils | 1.10.2 | CC0-1.0 | [xml-utils](https://github.com/DanielJDufour/xml-utils) |
| zstddec | 0.2.0 | MIT AND BSD-3-Clause | [zstddec](https://github.com/ygoe/zstddec) |

The package versions are pinned in `package-lock.json`. Consult each upstream repository/package for its complete license text and applicable notices. The geotiff.js MIT license text follows:

```text
The MIT License (MIT)

Copyright (c) 2015 EOX IT Services GmbH

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
