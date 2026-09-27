/* We Book Shows: small, dependency-free site script */
(function () {
  "use strict";
  var C = window.WBS_CONFIG || {};
  var EMAIL = (C.CONTACT_EMAIL || "").trim();
  var PHONE = (C.CONTACT_PHONE || "").trim();
  var validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(EMAIL);

  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  /* Year */
  $all(".js-year").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* Contact details from config */
  if (validEmail) {
    $all(".js-email").forEach(function (a) {
      a.href = "mailto:" + EMAIL;
      if (a.hasAttribute("data-show")) a.textContent = EMAIL;
    });
  }
  var TEL = (C.CONTACT_PHONE_TEL || PHONE.replace(/[^\d+]/g, "")).trim();
  var WHO = (C.BOOKING_CONTACT_NAME || "").trim();
  $all(".js-phone-row").forEach(function (r) { r.hidden = !PHONE; });
  if (PHONE) {
    $all(".js-phone").forEach(function (a) { a.href = "tel:" + TEL; a.textContent = PHONE; });
    $all(".js-phone-who").forEach(function (el) { el.textContent = WHO ? "Bookings: " + WHO + "," : "Bookings:"; });
  }

  /* Lite YouTube: load the iframe only on click */
  $all("button.yt").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-yt");
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) + "?autoplay=1&rel=0";
      f.title = btn.getAttribute("aria-label").replace(/^Play video: /, "");
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
      f.referrerPolicy = "strict-origin-when-cross-origin";
      f.allowFullscreen = true;
      btn.replaceWith(f);
    });
  });

  /* Roster filters */
  var grid = document.getElementById("roster-grid");
  if (grid) {
    var btns = $all(".chip-btn");
    var empty = document.querySelector(".empty");
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-filter"), shown = 0;
        btns.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        $all(".card", grid).forEach(function (c) {
          var ok = f === "all" || (" " + c.getAttribute("data-good") + " ").indexOf(" " + f + " ") > -1;
          c.hidden = !ok; if (ok) shown++;
        });
        if (empty) empty.hidden = shown > 0;
      });
    });
  }

  /* Pre-select artist on booking form from ?artist=slug */
  try {
    var q = new URLSearchParams(location.search).get("artist");
    if (q) $all('input[name="artist_interest"]').forEach(function (i) { if (i.getAttribute("data-slug") === q) i.checked = true; });
  } catch (e) { /* old browser: ignore */ }

  /* Forms */
  function collect(form) {
    var data = {}, order = [];
    $all("input, select, textarea", form).forEach(function (el) {
      if (!el.name || el.name === "_honey") return;
      if (el.type === "checkbox") {
        if (!el.checked) return;
        data[el.name] = data[el.name] ? data[el.name] + ", " + el.value : el.value;
      } else {
        data[el.name] = el.value.trim();
      }
      if (order.indexOf(el.name) < 0) order.push(el.name);
    });
    return { data: data, order: order };
  }
  function labelFor(form, name) {
    var el = form.querySelector('label[for="' + name + '"]');
    if (!el) {
      var input = form.querySelector('[name="' + name + '"]');
      var fs = input && input.closest("fieldset");
      el = fs && fs.querySelector("legend");
    }
    return el && el.firstChild ? el.firstChild.textContent.trim() : name;
  }
  function mailtoHref(form, subject, payload) {
    var lines = payload.order.map(function (k) { return labelFor(form, k) + ": " + (payload.data[k] || "-"); });
    return "mailto:" + EMAIL + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n") + "\n\n(Sent from webookshows.com)");
  }
  function endpoint() {
    var p = (C.FORM_PROVIDER || "mailto").toLowerCase();
    if (p === "formsubmit" && validEmail) return { url: "https://formsubmit.co/ajax/" + encodeURIComponent(C.FORMSUBMIT_ALIAS || EMAIL), kind: p };
    if (p === "formspree" && C.FORMSPREE_ID) return { url: "https://formspree.io/f/" + encodeURIComponent(C.FORMSPREE_ID), kind: p };
    return null;
  }

  $all("form.js-form").forEach(function (form) {
    var status = form.querySelector(".form-status");
    var btn = form.querySelector('button[type="submit"]');
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      status.className = "form-status";
      // honeypot
      var hp = form.querySelector('input[name="_honey"]');
      if (hp && hp.value) return;
      // validation
      var bad = $all("[required]", form).filter(function (el) { return !el.checkValidity(); });
      $all(".invalid", form).forEach(function (el) { el.classList.remove("invalid"); });
      if (bad.length) {
        bad.forEach(function (el) { el.classList.add("invalid"); el.setAttribute("aria-invalid", "true"); });
        status.textContent = "Please fill in the highlighted fields.";
        status.classList.add("err");
        bad[0].focus();
        return;
      }
      $all("[aria-invalid]", form).forEach(function (el) { el.removeAttribute("aria-invalid"); });

      var subject = form.getAttribute("data-subject") || "Website inquiry";
      var payload = collect(form);
      var ep = endpoint();

      if (!ep) {
        if (!validEmail) { status.textContent = "Our inbox isn't set up yet. Please check back soon."; status.classList.add("err"); return; }
        window.location.href = mailtoHref(form, subject, payload);
        status.textContent = "Opening your email app. Just press send.";
        return;
      }

      var body = {};
      payload.order.forEach(function (k) { body[labelFor(form, k)] = payload.data[k]; });
      if (payload.data.email) body.email = payload.data.email;          // lets the service set Reply-To
      else if (/@/.test(payload.data.contact || "")) body.email = payload.data.contact;
      body._subject = subject;
      if (ep.kind === "formsubmit") { body._template = "table"; body._captcha = "false"; }

      btn.disabled = true; btn.textContent = "Sending…";
      fetch(ep.url, { method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(body) })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          var ok = res.ok && !(res.j && (res.j.success === "false" || res.j.success === false));
          if (!ok) throw new Error((res.j && res.j.message) || "send failed");
          form.reset();
          status.textContent = "Thanks, your message is on its way. We'll be in touch soon.";
          status.classList.add("ok");
        })
        .catch(function () {
          status.innerHTML = "";
          status.classList.add("err");
          var a = document.createElement("a");
          a.href = mailtoHref(form, subject, payload);
          a.textContent = "send it by email instead";
          status.appendChild(document.createTextNode("We couldn't send that just now. Please "));
          status.appendChild(a);
          status.appendChild(document.createTextNode(" (your details are pre-filled)."));
        })
        .then(function () { btn.disabled = false; btn.textContent = form.getAttribute("data-kind") === "artist" ? "Send submission" : "Send inquiry"; });
    });
  });
})();
