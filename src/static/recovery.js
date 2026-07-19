(function () {
  var form = document.getElementById("recovery-form");
  if (!form) return;

  var BODY_REGIONS = [
    ["Head & neck", "head_face", "Head / face"], ["Head & neck", "jaw", "Jaw"], ["Head & neck", "neck", "Neck"], ["Head & neck", "collarbones", "Collarbones"],
    ["Upper body", "shoulders", "Shoulders"], ["Upper body", "biceps_triceps", "Biceps / triceps"], ["Upper body", "elbows", "Elbows"], ["Upper body", "forearms", "Forearms"], ["Upper body", "wrists_hands", "Wrists / hands"], ["Upper body", "chest", "Chest"], ["Upper body", "ribs", "Ribs / side body"], ["Upper body", "abdomen", "Abdomen"],
    ["Back & pelvis", "upper_back", "Upper back"], ["Back & pelvis", "mid_back", "Mid back"], ["Back & pelvis", "lower_back", "Lower back"], ["Back & pelvis", "sacrum_si", "Sacrum / SI joint"], ["Back & pelvis", "hips", "Outer hips"], ["Back & pelvis", "hip_flexors", "Hip flexors"], ["Back & pelvis", "glutes", "Glutes"], ["Back & pelvis", "groin_adductors", "Groin / adductors"],
    ["Legs & feet", "quads", "Quads"], ["Legs & feet", "inner_thighs", "Inner thighs"], ["Legs & feet", "outer_thighs", "Outer thighs / IT band"], ["Legs & feet", "hamstrings", "Hamstrings"], ["Legs & feet", "kneecap", "Kneecap"], ["Legs & feet", "inner_knee", "Inner knee"], ["Legs & feet", "outer_knee", "Outer knee"], ["Legs & feet", "shins", "Shins"], ["Legs & feet", "calves", "Calves"], ["Legs & feet", "achilles", "Achilles"], ["Legs & feet", "ankles", "Ankles"], ["Legs & feet", "heels", "Heels"], ["Legs & feet", "feet", "Feet / arches"], ["Legs & feet", "toes", "Toes"],
  ];
  var REGION_TRANSFORMS = {
    hips: "translate(0 226) scale(1 1.3) translate(0 -226)",
    hip_flexors: "translate(0 226) scale(1 1.3) translate(0 -226)",
    glutes: "translate(0 226) scale(1 1.3) translate(0 -226)",
    groin_adductors: "translate(0 226) scale(1 1.3) translate(0 -226)",
    quads: "translate(0 290) scale(1 1.265) translate(0 -267)",
    inner_thighs: "translate(0 290) scale(1 1.265) translate(0 -267)",
    outer_thighs: "translate(0 290) scale(1 1.265) translate(0 -267)",
    hamstrings: "translate(0 290) scale(1 1.265) translate(0 -267)",
    kneecap: "translate(0 40)",
    inner_knee: "translate(0 40)",
    outer_knee: "translate(0 40)",
    shins: "translate(0 411) scale(1 1.1) translate(0 -376)",
    calves: "translate(0 411) scale(1 1.1) translate(0 -376)",
    achilles: "translate(0 27)",
    ankles: "translate(0 27)",
    heels: "translate(0 535) scale(1 .85) translate(0 -525)",
    feet: "translate(0 535) scale(1 .85) translate(0 -525)",
    toes: "translate(0 535) scale(1 .85) translate(0 -525)",
  };

  function labelFor(area) {
    var found = BODY_REGIONS.find(function (region) { return region[1] === area; });
    return found ? found[2] : area;
  }

  // Local interactive silhouette, informed by the public-domain Wikimedia
  // Commons "Human body silhouette.svg" reference. Hotspots remain inline so
  // they scale cleanly and do not depend on a third-party image request.
  // Proportion landmarks use a 70-unit head: chin 80, bust 150, waist 220,
  // crotch 290, mid-thigh 325, knees 395, mid-calf 465, feet 570-575.
  function anatomySvg() {
    return `<svg class="mannequin detailed-mannequin" viewBox="30 0 153 590" overflow="hidden" aria-hidden="true">
      <g class="body-shell body-view-front">
        <ellipse cx="107" cy="45" rx="23" ry="35"/>
        <path d="M94 77 C96 88 96 95 91 101 C77 103 66 107 58 115 C54 132 55 153 60 177 C65 198 70 218 67 239 C65 253 62 269 67 279 C79 286 93 290 107 290 C121 290 135 286 147 279 C152 269 149 253 147 239 C144 218 149 198 154 177 C159 153 160 132 156 115 C148 107 137 103 123 101 C118 95 118 88 120 77 C113 84 101 84 94 77 Z"/>
        <path d="M59 113 C49 120 45 133 43 150 L38 191 C37 208 34 224 31 239 C30 247 34 252 42 253 C48 249 51 243 53 235 L60 198 C63 181 64 161 66 142 C68 128 66 119 59 113 Z"/>
        <path d="M155 113 C165 120 169 133 171 150 L176 191 C177 208 180 224 183 239 C184 247 180 252 172 253 C166 249 163 243 161 235 L154 198 C151 181 150 161 148 142 C146 128 148 119 155 113 Z"/>
        <path d="M68 286 C61 319 61 362 64 395 C62 420 62 447 65 465 C64 491 62 521 64 550 C58 558 58 569 68 573 L82 571 C80 559 78 548 78 535 L79 468 C81 443 82 419 80 396 C84 360 86 320 84 290 Z"/>
        <path d="M146 286 C153 319 153 362 150 395 C152 420 152 447 149 465 C150 491 152 521 150 550 C156 558 156 569 146 573 L132 571 C134 559 136 548 136 535 L135 468 C133 443 132 419 134 396 C130 360 128 320 130 290 Z"/>
      </g>
      <g class="body-shell body-view-back">
        <ellipse cx="258" cy="45" rx="23" ry="35"/>
        <path d="M245 77 C247 88 247 95 242 101 C228 103 217 107 209 115 C205 132 206 153 211 177 C216 198 221 218 218 239 C216 253 213 269 218 279 C230 286 244 290 258 290 C272 290 286 286 298 279 C303 269 300 253 298 239 C295 218 300 198 305 177 C310 153 311 132 307 115 C299 107 288 103 274 101 C269 95 269 88 271 77 C264 84 252 84 245 77 Z"/>
        <path d="M210 113 C200 120 196 133 194 150 L189 191 C188 208 185 224 183 239 C182 247 186 252 194 253 C200 249 203 243 205 235 L211 198 C214 181 215 161 217 142 C219 128 217 119 210 113 Z"/>
        <path d="M306 113 C316 120 320 133 322 150 L327 191 C328 208 331 224 334 239 C335 247 331 252 323 253 C317 249 314 243 312 235 L305 198 C302 181 301 161 299 142 C297 128 299 119 306 113 Z"/>
        <path d="M219 286 C212 319 212 362 215 395 C213 420 213 447 216 465 C215 491 213 521 215 550 C209 558 209 569 219 573 L233 571 C231 559 229 548 229 535 L230 468 C232 443 233 419 231 396 C235 360 237 320 235 290 Z"/>
        <path d="M297 286 C304 319 304 362 301 395 C303 420 303 447 300 465 C301 491 303 521 301 550 C307 558 307 569 297 573 L283 571 C285 559 287 548 287 535 L286 468 C284 443 283 419 285 396 C281 360 279 320 281 290 Z"/>
      </g>
      <g data-area="head_face" class="body-region"><ellipse cx="107" cy="45" rx="21" ry="33"/><ellipse cx="258" cy="45" rx="21" ry="33"/></g><g data-area="jaw" class="body-region"><path d="M98 68 Q107 80 116 68 L113 77 Q107 84 101 77Z"/></g><g data-area="neck" class="body-region"><path d="M95 78 C92 88 90 96 90 103 L124 103 C124 96 122 88 119 78 Q107 86 95 78Z"/><path d="M246 78 C243 88 241 96 241 103 L275 103 C275 96 273 88 270 78 Q258 86 246 78Z"/></g>
      <g data-area="collarbones" class="body-region"><path d="M66 112 Q107 97 148 112 L145 119 Q107 106 69 119Z"/></g><g data-area="shoulders" class="body-region"><path d="M65 110 C55 108 46 113 41 124 C38 132 38 138 41 144 L58 138 C56 128 58 118 68 111Z"/><path d="M149 110 C159 108 168 113 173 124 C176 132 176 138 173 144 L156 138 C158 128 156 118 146 111Z"/><path d="M216 110 C206 108 197 113 192 124 C189 132 189 138 192 144 L209 138 C207 128 209 118 219 111Z"/><path d="M300 110 C310 108 319 113 324 124 C327 132 327 138 324 144 L307 138 C309 128 307 118 297 111Z"/></g>
      <g data-area="biceps_triceps" class="body-region"><path d="M40 145 C37 156 36 168 39 180 L57 184 C56 170 57 156 58 146 Q49 142 40 145Z"/><path d="M174 145 C177 156 178 168 175 180 L157 184 C158 170 157 156 156 146 Q165 142 174 145Z"/><path d="M191 145 C188 156 187 168 190 180 L208 184 C207 170 208 156 209 146 Q200 142 191 145Z"/><path d="M325 145 C328 156 329 168 326 180 L308 184 C309 170 308 156 307 146 Q316 142 325 145Z"/></g><g data-area="elbows" class="body-region"><path d="M38 182 Q35 194 39 204 L58 208 Q61 196 57 186 Q47 180 38 182Z"/><path d="M176 182 Q179 194 175 204 L156 208 Q153 196 157 186 Q167 180 176 182Z"/><path d="M189 182 Q186 194 190 204 L209 208 Q212 196 208 186 Q198 180 189 182Z"/><path d="M327 182 Q330 194 326 204 L307 208 Q304 196 308 186 Q318 180 327 182Z"/></g><g data-area="forearms" class="body-region"><path d="M40 206 C37 214 36 222 38 230 L56 233 C57 224 58 216 60 208 Q50 204 40 206Z"/><path d="M174 206 C177 214 178 222 176 230 L158 233 C157 224 156 216 154 208 Q164 204 174 206Z"/><path d="M191 206 C188 214 187 222 189 230 L207 233 C208 224 209 216 211 208 Q201 204 191 206Z"/><path d="M325 206 C328 214 329 222 327 230 L309 233 C308 224 307 216 305 208 Q315 204 325 206Z"/></g><g data-area="wrists_hands" class="body-region"><path d="M36 231 Q31 240 37 248 Q45 253 53 248 Q57 240 53 231 Q44 227 36 231Z"/><path d="M178 231 Q183 240 177 248 Q169 253 161 248 Q157 240 161 231 Q170 227 178 231Z"/><path d="M187 231 Q182 240 188 248 Q196 253 204 248 Q208 240 204 231 Q195 227 187 231Z"/><path d="M329 231 Q334 240 328 248 Q320 253 312 248 Q316 240 312 231 Q321 227 329 231Z"/></g>
      <g data-area="chest" class="body-region"><path d="M68 118 C63 126 62 133 64 140 C66 147 70 152 75 155 L139 155 C144 152 148 147 150 140 C152 133 151 126 146 118 Q107 111 68 118Z"/></g><g data-area="ribs" class="body-region"><path d="M75 155 Q70 168 79 181 L135 181 Q144 168 139 155 Q107 162 75 155Z"/></g><g data-area="abdomen" class="body-region"><path d="M79 181 Q75 197 82 210 Q80 218 81 226 L133 226 Q134 218 132 210 Q139 197 135 181 Q107 188 79 181Z"/></g>
      <g data-area="upper_back" class="body-region"><path d="M219 118 Q258 108 297 118 L294 152 Q258 158 222 152Z"/></g><g data-area="mid_back" class="body-region"><path d="M222 152 Q258 160 294 152 L291 181 Q258 188 225 181Z"/></g><g data-area="lower_back" class="body-region"><path d="M225 181 Q258 190 291 181 Q288 205 285 226 L231 226 Q228 205 225 181Z"/></g><g data-area="sacrum_si" class="body-region"><path d="M231 226 Q258 234 285 226 L283 246 Q258 254 233 246Z"/></g>
      <g data-area="hips" class="body-region"><path d="M72 226 Q65 240 68 254 C70 260 74 263 79 264 L86 250 Q82 238 81 226Z"/><path d="M142 226 Q149 240 146 254 C144 260 140 263 135 264 L128 250 Q132 238 133 226Z"/><path d="M223 226 Q216 240 219 254 C221 260 225 263 230 264 L237 250 Q233 238 232 226Z"/><path d="M293 226 Q300 240 297 254 C295 260 291 263 286 264 L279 250 Q283 238 284 226Z"/></g><g data-area="hip_flexors" class="body-region"><path d="M81 227 Q107 233 133 227 L133 250 Q107 256 81 250Z"/></g><g data-area="glutes" class="body-region"><path d="M225 246 Q258 228 291 246 L293 262 Q258 274 223 262Z"/></g><g data-area="groin_adductors" class="body-region"><path d="M90 252 Q107 262 124 252 Q118 268 107 270 Q96 268 90 252Z"/></g>
      <g data-area="quads" class="body-region"><path d="M68 267 C64 288 63 310 66 332 C67 340 70 346 76 349 L96 346 C99 322 100 296 99 270 Q83 262 68 267Z"/><path d="M146 267 C150 288 151 310 148 332 C147 340 144 346 138 349 L118 346 C115 322 114 296 115 270 Q131 262 146 267Z"/></g><g data-area="inner_thighs" class="body-region"><path d="M96 270 Q93 300 94 330 Q95 340 100 348 L104 344 C102 320 102 296 101 271 Q99 270 96 270Z"/><path d="M118 271 Q116 296 116 320 C114 344 112 344 110 348 L114 344 Q109 340 110 330 Q111 300 108 270 Q113 270 118 271Z"/></g><g data-area="outer_thighs" class="body-region"><path d="M68 268 Q64 300 66 332 Q67 342 72 349 L79 346 C75 322 74 296 76 270 Q72 268 68 268Z"/><path d="M146 268 Q150 300 148 332 Q147 342 142 349 L135 346 C139 322 140 296 138 270 Q142 268 146 268Z"/></g><g data-area="hamstrings" class="body-region"><path d="M219 267 C215 289 214 311 217 333 C218 341 221 347 227 350 L247 347 C250 323 251 297 250 271 Q234 263 219 267Z"/><path d="M297 267 C301 289 302 311 299 333 C298 341 295 347 289 350 L269 347 C266 323 265 297 266 271 Q282 263 297 267Z"/></g>
      <g data-area="kneecap" class="body-region"><path d="M72 350 Q85 344 98 350 Q100 362 98 374 Q85 380 72 374 Q70 362 72 350Z"/><path d="M116 350 Q129 344 142 350 Q144 362 142 374 Q129 380 116 374 Q114 362 116 350Z"/><path d="M223 350 Q236 344 249 350 Q251 362 249 374 Q236 380 223 374 Q221 362 223 350Z"/><path d="M267 350 Q280 344 293 350 Q295 362 293 374 Q280 380 267 374 Q265 362 267 350Z"/></g><g data-area="inner_knee" class="body-region"><path d="M97 351 Q94 362 97 373 L106 371 Q104 362 106 353Z"/><path d="M117 353 Q115 362 117 371 L108 373 Q106 362 108 351Z"/><path d="M248 351 Q245 362 248 373 L257 371 Q255 362 257 353Z"/><path d="M268 353 Q266 362 268 371 L259 373 Q257 362 259 351Z"/></g><g data-area="outer_knee" class="body-region"><path d="M62 353 Q60 362 62 371 L71 373 Q69 362 71 351Z"/><path d="M152 353 Q154 362 152 371 L143 373 Q145 362 143 351Z"/><path d="M213 353 Q211 362 213 371 L222 373 Q220 362 222 351Z"/><path d="M303 353 Q305 362 303 371 L294 373 Q296 362 294 351Z"/></g>
      <g data-area="shins" class="body-region"><path d="M69 376 C65 405 64 435 66 462 C67 468 69 472 72 476 L92 474 C95 440 96 405 95 378 Q82 372 69 376Z"/><path d="M145 376 C149 405 150 435 148 462 C147 468 145 472 142 476 L122 474 C119 440 118 405 119 378 Q132 372 145 376Z"/></g><g data-area="calves" class="body-region"><path d="M217 376 C212 400 210 424 214 448 C216 458 220 466 226 472 L246 468 C248 440 249 408 247 378 Q232 370 217 376Z"/><path d="M299 376 C304 400 306 424 302 448 C300 458 296 466 290 472 L270 468 C268 440 267 408 269 378 Q284 370 299 376Z"/></g><g data-area="achilles" class="body-region"><path d="M68 478 Q65 495 68 512 L78 510 Q76 495 77 480Z"/><path d="M146 480 Q149 495 146 512 L136 510 Q134 495 136 478Z"/><path d="M219 478 Q216 495 219 512 L229 510 Q227 495 228 480Z"/><path d="M297 480 Q300 495 297 512 L287 510 Q285 495 287 478Z"/></g>
      <g data-area="ankles" class="body-region"><path d="M66 493 Q63 503 66 512 L92 512 Q95 503 93 493 Q79 489 66 493Z"/><path d="M148 493 Q151 503 148 512 L122 512 Q119 503 121 493 Q135 489 148 493Z"/><path d="M217 493 Q214 503 217 512 L243 512 Q246 503 244 493 Q230 489 217 493Z"/><path d="M299 493 Q302 503 299 512 L273 512 Q270 503 272 493 Q286 489 299 493Z"/></g><g data-area="heels" class="body-region"><path d="M63 525 Q58 534 63 542 L90 540 Q93 532 90 524 Q76 520 63 525Z"/><path d="M151 525 Q156 534 151 542 L124 540 Q121 532 124 524 Q138 520 151 525Z"/><path d="M214 525 Q209 534 214 542 L241 540 Q244 532 241 524 Q227 520 214 525Z"/><path d="M302 525 Q307 534 302 542 L275 540 Q272 532 275 524 Q289 520 302 525Z"/></g><g data-area="feet" class="body-region"><path d="M58 545 Q52 555 60 561 Q78 566 98 561 Q106 555 100 545 Q79 539 58 545Z"/><path d="M156 545 Q162 555 154 561 Q136 566 116 561 Q108 555 114 545 Q135 539 156 545Z"/><path d="M209 545 Q203 555 211 561 Q229 566 249 561 Q257 555 251 545 Q230 539 209 545Z"/><path d="M307 545 Q313 555 305 561 Q287 566 267 561 Q259 555 265 545 Q286 539 307 545Z"/></g><g data-area="toes" class="body-region"><path d="M88 559 Q84 566 90 570 Q98 573 106 570 Q110 566 106 560 Q97 556 88 559Z"/><path d="M136 560 Q140 566 134 570 Q126 573 118 570 Q114 566 118 559 Q127 556 136 560Z"/><path d="M239 559 Q235 566 241 570 Q249 573 257 570 Q261 566 257 560 Q248 556 239 559Z"/><path d="M287 560 Q291 566 285 570 Q277 573 269 570 Q265 566 269 559 Q278 556 287 560Z"/></g>
    </svg>`;
  }

  var oldSvg = document.querySelector(".mannequin");
  oldSvg.outerHTML = anatomySvg();
  var mannequin = document.querySelector(".mannequin");
  document.querySelectorAll(".mannequin [data-area]").forEach(function (region) {
    Array.from(region.children).forEach(function (shape) {
      var box = shape.getBBox();
      shape.classList.add(box.x + box.width / 2 < 183 ? "body-view-front" : "body-view-back");
    });
    if (REGION_TRANSFORMS[region.dataset.area]) region.setAttribute("transform", REGION_TRANSFORMS[region.dataset.area]);
    var title = document.createElementNS("http://www.w3.org/2000/svg", "title");
    title.textContent = labelFor(region.dataset.area);
    region.prepend(title);
  });
  var bodyHelp = document.getElementById("body-help");
  var bodyView = "front";
  mannequin.dataset.activeBodyView = bodyView;
  var bodyZoom = 1;
  var bodyPanX = 0;
  var bodyPanY = 0;
  var zoomLevel = document.querySelector("[data-body-zoom-level]");
  var viewBounds = {
    front: { x: 30, width: 153 },
    back: { x: 183, width: 152 },
  };

  function clamp(value, minimum, maximum) { return Math.max(minimum, Math.min(maximum, value)); }

  function renderBodyMap() {
    var bounds = viewBounds[bodyView];
    var width = bounds.width / bodyZoom;
    var height = 590 / bodyZoom;
    var maxPanX = Math.max(0, (bounds.width - width) / 2);
    var maxPanY = Math.max(0, (590 - height) / 2);
    bodyPanX = clamp(bodyPanX, -maxPanX, maxPanX);
    bodyPanY = clamp(bodyPanY, -maxPanY, maxPanY);
    var x = bounds.x + (bounds.width - width) / 2 + bodyPanX;
    var y = (590 - height) / 2 + bodyPanY;
    mannequin.setAttribute("viewBox", [x, y, width, height].join(" "));
    mannequin.classList.toggle("is-zoomed", bodyZoom > 1);
    if (zoomLevel) zoomLevel.textContent = Math.round(bodyZoom * 100) + "%";
  }

  function setBodyZoom(nextZoom) {
    bodyZoom = clamp(nextZoom, 1, 2.5);
    if (bodyZoom === 1) { bodyPanX = 0; bodyPanY = 0; }
    renderBodyMap();
  }

  document.querySelectorAll("[data-body-view]").forEach(function (button) {
    button.addEventListener("click", function () {
      bodyView = button.dataset.bodyView;
      mannequin.dataset.activeBodyView = bodyView;
      bodyZoom = 1;
      bodyPanX = 0;
      bodyPanY = 0;
      renderBodyMap();
      document.querySelectorAll("[data-body-view]").forEach(function (item) {
        item.setAttribute("aria-pressed", String(item === button));
      });
      bodyHelp.textContent = bodyView === "back" ? "Back view. Choose a highlighted area or browse the labels below." : "Front view. Choose a highlighted area or browse the labels below.";
    });
  });

  document.querySelectorAll("[data-body-zoom]").forEach(function (button) {
    button.addEventListener("click", function () {
      if (button.dataset.bodyZoom === "in") setBodyZoom(bodyZoom + .25);
      else if (button.dataset.bodyZoom === "out") setBodyZoom(bodyZoom - .25);
      else setBodyZoom(1);
    });
  });
  mannequin.addEventListener("wheel", function (event) {
    event.preventDefault();
    setBodyZoom(bodyZoom + (event.deltaY < 0 ? .25 : -.25));
  }, { passive: false });

  var dragState = null;
  mannequin.addEventListener("pointerdown", function (event) {
    if (bodyZoom === 1 || event.target.closest("[data-area]")) return;
    dragState = { x: event.clientX, y: event.clientY, panX: bodyPanX, panY: bodyPanY };
    mannequin.setPointerCapture(event.pointerId);
    mannequin.classList.add("is-dragging");
  });
  mannequin.addEventListener("pointermove", function (event) {
    if (!dragState) return;
    var box = mannequin.getBoundingClientRect();
    var bounds = viewBounds[bodyView];
    bodyPanX = dragState.panX - (event.clientX - dragState.x) * (bounds.width / bodyZoom) / box.width;
    bodyPanY = dragState.panY - (event.clientY - dragState.y) * (590 / bodyZoom) / box.height;
    renderBodyMap();
  });
  function stopBodyDrag() { dragState = null; mannequin.classList.remove("is-dragging"); }
  mannequin.addEventListener("pointerup", stopBodyDrag);
  mannequin.addEventListener("pointercancel", stopBodyDrag);
  renderBodyMap();
  var regionList = document.getElementById("region-list");
  var currentGroup = "";
  regionList.innerHTML = BODY_REGIONS.map(function (region) {
    var heading = region[0] !== currentGroup ? (currentGroup = region[0], `<p class="region-group">${currentGroup}</p>`) : "";
    return heading + `<button type="button" data-area="${region[1]}" aria-pressed="false">${region[2]}</button>`;
  }).join("");
  var notesLabel = form.querySelector("textarea[name=notes]").closest("label");
  notesLabel.insertAdjacentHTML("beforebegin", `<div class="detail-grid"><label>Which side?<select name="side"><option value="both">Both sides</option><option value="left">Left side</option><option value="right">Right side</option><option value="center">Center</option></select></label><label>Exact spot (optional)<input name="location_detail" maxlength="240" placeholder="e.g. outside, below kneecap, near joint"></label></div>`);

  var selected = new Set();
  var selectorButtons = document.querySelectorAll("[data-area]");
  var selectedAreas = document.getElementById("selected-areas");
  var pain = document.getElementById("pain-level");
  var painOutput = document.getElementById("pain-output");
  var result = document.getElementById("guidance-result");
  var steps = Array.from(form.querySelectorAll("[data-recovery-step]"));
  var stepIndicators = Array.from(document.querySelectorAll("[data-step-indicator]"));

  function showStep(number, focusHeading) {
    steps.forEach(function (step) {
      step.hidden = Number(step.dataset.recoveryStep) !== number;
    });
    stepIndicators.forEach(function (indicator) {
      var active = Number(indicator.dataset.stepIndicator) === number;
      indicator.classList.toggle("is-active", active);
      if (active) indicator.setAttribute("aria-current", "step");
      else indicator.removeAttribute("aria-current");
    });
    if (focusHeading) {
      var heading = form.querySelector('[data-recovery-step="' + number + '"] h3');
      if (heading) { heading.tabIndex = -1; heading.focus(); }
    }
  }

  form.querySelectorAll("[data-step-next]").forEach(function (button) {
    button.addEventListener("click", function () {
      if (button.dataset.stepNext === "2" && !selected.size) return;
      showStep(Number(button.dataset.stepNext), true);
    });
  });
  form.querySelectorAll("[data-step-back]").forEach(function (button) {
    button.addEventListener("click", function () { showStep(Number(button.dataset.stepBack), true); });
  });

  function updateSelection() {
    selectorButtons.forEach(function (element) { var active = selected.has(element.dataset.area); element.classList.toggle("is-selected", active); if (element.tagName === "BUTTON") element.setAttribute("aria-pressed", active); });
    selectedAreas.textContent = selected.size ? Array.from(selected).map(labelFor).join(" · ") : "Select one or more body regions";
    selectedAreas.classList.toggle("has-selection", Boolean(selected.size));
    selectedAreas.removeAttribute("role");
    var firstNext = form.querySelector('[data-step-next="2"]');
    if (firstNext) firstNext.disabled = !selected.size;
  }
  selectorButtons.forEach(function (element) { element.addEventListener("click", function () { var area = element.dataset.area; if (selected.has(area)) selected.delete(area); else selected.add(area); updateSelection(); }); });
  pain.addEventListener("input", function () { painOutput.textContent = pain.value + " / 10"; });
  function showResult(title, message, urgent, references, anchors) {
    result.className = "guidance-result" + (urgent ? " urgent" : "");
    result.setAttribute("role", urgent ? "alert" : "status");
    result.setAttribute("aria-live", urgent ? "assertive" : "polite");
    result.replaceChildren();
    var heading = document.createElement("p"); heading.className = "section-kicker"; heading.textContent = title;
    var body = document.createElement("p"); body.textContent = message;
    result.append(heading, body);
    if (references && references.length) {
      var refKicker = document.createElement("p");
      refKicker.className = "section-kicker guidance-refs-kicker";
      refKicker.textContent = "Region-matched reading (educational)";
      var list = document.createElement("ul");
      list.className = "guidance-refs";
      references.forEach(function (ref) {
        var item = document.createElement("li");
        var link = document.createElement("a");
        link.href = ref.url; link.target = "_blank"; link.rel = "noreferrer";
        link.textContent = ref.label;
        item.appendChild(link);
        list.appendChild(item);
      });
      var browse = document.createElement("p");
      browse.className = "guidance-refs-browse";
      var browseLink = document.createElement("a");
      browseLink.href = "/research#" + ((anchors && anchors[0]) || "");
      browseLink.textContent = "Browse the full research library";
      browse.appendChild(browseLink);
      result.append(refKicker, list, browse);
    }
    result.hidden = false;
    if (urgent) { result.tabIndex = -1; result.focus(); }
  }
  form.addEventListener("submit", async function (event) {
    event.preventDefault(); if (!selected.size) { showStep(1, false); selectedAreas.textContent = "Choose at least one body region to continue."; selectedAreas.setAttribute("role", "alert"); selectedAreas.tabIndex = -1; selectedAreas.focus(); return; }
    var button = form.querySelector("button[type=submit]"); button.disabled = true; button.textContent = "Creating check-in…"; result.hidden = true;
    var values = new FormData(form); var payload = { body_areas: Array.from(selected), pain_level: values.get("pain_level"), onset: values.get("onset"), sensation: values.getAll("sensation"), triggers: values.getAll("triggers"), side: values.get("side"), location_detail: values.get("location_detail"), notes: values.get("notes") };
    try { var csrf = document.querySelector('meta[name="csrf-token"]'); var response = await fetch("/api/recovery/checkins", { method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf ? csrf.content : "" }, body: JSON.stringify(payload) }); var data = await response.json(); if (!response.ok) throw new Error(data.error || "We could not create that check-in."); showResult(data.urgent ? "Safety first" : "Your recovery note", data.guidance, data.urgent, data.references, data.research_anchors); var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches; result.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "nearest" }); } catch (error) { showResult("Check-in unavailable", error.message, true); } finally { button.disabled = false; button.textContent = "Create recovery check-in"; }
  });
}());
