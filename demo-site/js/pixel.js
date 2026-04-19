(function () {
  const API_BASE = "http://localhost:8000";
  const UID_KEY = "pixel_lab_anonymous_user_id";
  const SESSION_KEY = "pixel_lab_session_id";

  function uuidv4() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      const r = (Math.random() * 16) | 0;
      const v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function getOrCreateStorageValue(key) {
    let value = localStorage.getItem(key);
    if (!value) {
      value = uuidv4();
      localStorage.setItem(key, value);
    }
    return value;
  }

  function getUtmParams() {
    const params = new URLSearchParams(window.location.search);
    return {
      utm_source: params.get("utm_source"),
      utm_medium: params.get("utm_medium"),
      utm_campaign: params.get("utm_campaign"),
      utm_term: params.get("utm_term"),
      utm_content: params.get("utm_content")
    };
  }

  function basePayload() {
    return {
      page_url: window.location.href,
      referrer: document.referrer || null,
      session_id: getOrCreateStorageValue(SESSION_KEY),
      anonymous_user_id: getOrCreateStorageValue(UID_KEY),
      user_agent: navigator.userAgent,
      language: navigator.language,
      screen_width: window.screen.width,
      screen_height: window.screen.height,
      event_time: new Date().toISOString(),
      ...getUtmParams()
    };
  }

  function sendToTrackEndpoint(eventName, payload) {
    const finalPayload = {
      event_name: eventName,
      ...basePayload(),
      payload_json: payload || {}
    };

    return fetch(`${API_BASE}/track`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(finalPayload)
    }).catch(function (err) {
      console.error("track failed", err);
    });
  }

  // Classic image pixel helper to demonstrate GET-based tracking.
  function sendImagePixel(eventName) {
    const payload = basePayload();
    const params = new URLSearchParams({
      event: eventName,
      page: payload.page_url,
      session_id: payload.session_id,
      uid: payload.anonymous_user_id,
      utm_source: payload.utm_source || "",
      utm_medium: payload.utm_medium || "",
      utm_campaign: payload.utm_campaign || "",
      utm_term: payload.utm_term || "",
      utm_content: payload.utm_content || ""
    });

    const img = new Image();
    img.src = `${API_BASE}/pixel?${params.toString()}`;
  }

  window.myPixel = {
    track: sendToTrackEndpoint,
    pixel: sendImagePixel,
    getAnonymousUserId: function () {
      return getOrCreateStorageValue(UID_KEY);
    },
    getSessionId: function () {
      return getOrCreateStorageValue(SESSION_KEY);
    }
  };

  window.addEventListener("load", function () {
    sendToTrackEndpoint("page_view", { auto: true });
  });
})();
