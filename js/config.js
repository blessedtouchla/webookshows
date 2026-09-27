/* ==========================================================================
   SITE CONFIG: the ONLY place contact details live.
   Change these values and every page + both forms update automatically.
   ========================================================================== */
window.WBS_CONFIG = {
  // Public contact email. Shown on the About/contact page and used as the
  // form destination. (Set Sept 2026.)
  CONTACT_EMAIL: "webookshows@yahoo.com",

  // Bookings phone line (approved Sept 2026). Leave CONTACT_PHONE "" to hide it everywhere.
  BOOKING_CONTACT_NAME: "Herman Watson",
  CONTACT_PHONE: "(323) 595-3611",       // as displayed
  CONTACT_PHONE_TEL: "+13235953611",     // used in the tel: link

  // Form delivery service:
  //   "formsubmit": https://formsubmit.co (no account; first submission sends
  //                  an activation email to CONTACT_EMAIL that must be clicked once)
  //   "formspree":   https://formspree.io (needs a form id in FORMSPREE_ID)
  //   "mailto":      no service; opens the visitor's email app pre-filled
  FORM_PROVIDER: "formsubmit",

  // Optional: after activating FormSubmit you can replace the email in the
  // endpoint with the random alias FormSubmit gives you (hides the address
  // from scrapers). Leave "" to use CONTACT_EMAIL.
  FORMSUBMIT_ALIAS: "",

  // Only used when FORM_PROVIDER is "formspree", e.g. "xayzabcd"
  FORMSPREE_ID: ""
};
