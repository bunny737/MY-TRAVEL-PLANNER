/* Google tag loader and event hooks. Configured only through data-* attributes on its own <script> tag
   (no inline script, no personal data). Events: whatsapp_click / call_click on [data-track] links,
   generate_lead on the thank-you page when the server marks a new lead. */
(function () {
  'use strict';

  var tag = document.querySelector('script[data-tracking]');
  if (!tag) { return; }
  var ga4 = tag.getAttribute('data-ga4-id') || '';
  var ads = tag.getAttribute('data-ads-id') || '';
  var primary = ga4 || ads;
  if (!primary) { return; }

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  if (ga4) { window.gtag('config', ga4); }
  if (ads) { window.gtag('config', ads); }

  var loader = document.createElement('script');
  loader.async = true;
  loader.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(primary);
  document.head.appendChild(loader);

  var pageType = tag.getAttribute('data-page-type') || '';

  // sendTo is "AW-ID/LABEL" for an Ads conversion, or empty when that conversion is not configured.
  // where / item are fixed labels from the server (which button, which page slug): never visitor data.
  function send(name, sendTo, where, item) {
    var params = { transport_type: 'beacon' };
    if (pageType) { params.page_type = pageType; }
    if (where) { params.cta_location = where; }
    if (item) { params.item_name = item; }
    window.gtag('event', name, params);
    if (sendTo) {
      window.gtag('event', 'conversion', { send_to: sendTo, transport_type: 'beacon' });
    }
  }

  document.addEventListener('click', function (event) {
    var el = event.target.closest ? event.target.closest('[data-track]') : null;
    if (el) {
      send(el.getAttribute('data-track'), el.getAttribute('data-ads-send-to') || '',
           el.getAttribute('data-where') || '', el.getAttribute('data-item') || '');
    }
  });

  var conversion = document.querySelector('[data-lead-conversion]');
  if (conversion) { send('generate_lead', conversion.getAttribute('data-ads-send-to') || ''); }
})();
