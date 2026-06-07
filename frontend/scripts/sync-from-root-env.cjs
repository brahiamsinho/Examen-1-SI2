/**
 * Lee MAILHOG_WEB_URL y FIREBASE_WEB_* del `.env` en la raíz del repo y genera
 * archivos en `src/environments/` (sin secretos ni URLs fijas en environment.ts).
 */
const fs = require("fs");
const path = require("path");

function loadEnvFile(absPath) {
  const env = {};
  if (!fs.existsSync(absPath)) return env;
  for (const line of fs.readFileSync(absPath, "utf8").split(/\r?\n/)) {
    if (!line || line.trim().startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq < 1) continue;
    const key = line.slice(0, eq).trim();
    let val = line.slice(eq + 1).trim();
    if (
      (val.startsWith('"') && val.endsWith('"')) ||
      (val.startsWith("'") && val.endsWith("'"))
    ) {
      val = val.slice(1, -1);
    }
    env[key] = val;
  }
  return env;
}

function envBool(raw) {
  if (raw === undefined || raw === null) return false;
  const s = String(raw).trim().toLowerCase();
  return s === "1" || s === "true" || s === "yes" || s === "on";
}

function pickEnv(rootEnv, key, buildEnvKey) {
  if (
    Object.prototype.hasOwnProperty.call(process.env, buildEnvKey) &&
    process.env[buildEnvKey] !== undefined
  ) {
    return String(process.env[buildEnvKey]).trim();
  }
  if (Object.prototype.hasOwnProperty.call(rootEnv, key)) {
    return String(rootEnv[key] ?? "").trim();
  }
  return "";
}

const frontendDir = path.resolve(__dirname, "..");
const repoRoot = path.resolve(frontendDir, "..");
const envPath = path.join(repoRoot, ".env");
const rootEnv = loadEnvFile(envPath);
const envDir = path.join(frontendDir, "src", "environments");

// --- MailHog ---
const hasBuildMailhog =
  Object.prototype.hasOwnProperty.call(process.env, "MAILHOG_WEB_URL") &&
  process.env.MAILHOG_WEB_URL !== undefined;

let mailhogRaw;
if (hasBuildMailhog) {
  mailhogRaw = String(process.env.MAILHOG_WEB_URL).trim();
} else {
  if (!Object.prototype.hasOwnProperty.call(rootEnv, "MAILHOG_WEB_URL")) {
    throw new Error(
      "[sync-from-root-env] Falta MAILHOG_WEB_URL: definila en " +
        envPath +
        " (clave MAILHOG_WEB_URL=...) o exportá MAILHOG_WEB_URL antes del build (Docker: build-arg). Podés dejarla vacía: MAILHOG_WEB_URL=",
    );
  }
  mailhogRaw = String(rootEnv.MAILHOG_WEB_URL ?? "").trim();
}

fs.writeFileSync(
  path.join(envDir, "mailhog-url.generated.ts"),
  `/* Archivo generado por scripts/sync-from-root-env.cjs — no editar a mano. */
export const mailhogWebUrl = ${JSON.stringify(mailhogRaw)};
`,
  "utf8",
);

// --- Firebase web (push CU19) ---
const fbEnabled = envBool(
  pickEnv(rootEnv, "FIREBASE_WEB_ENABLED", "FIREBASE_WEB_ENABLED"),
);
const fbConfig = {
  enabled: fbEnabled,
  apiKey: pickEnv(rootEnv, "FIREBASE_WEB_API_KEY", "FIREBASE_WEB_API_KEY"),
  authDomain: pickEnv(rootEnv, "FIREBASE_WEB_AUTH_DOMAIN", "FIREBASE_WEB_AUTH_DOMAIN"),
  projectId: pickEnv(rootEnv, "FIREBASE_WEB_PROJECT_ID", "FIREBASE_WEB_PROJECT_ID"),
  storageBucket: pickEnv(
    rootEnv,
    "FIREBASE_WEB_STORAGE_BUCKET",
    "FIREBASE_WEB_STORAGE_BUCKET",
  ),
  messagingSenderId: pickEnv(
    rootEnv,
    "FIREBASE_WEB_MESSAGING_SENDER_ID",
    "FIREBASE_WEB_MESSAGING_SENDER_ID",
  ),
  appId: pickEnv(rootEnv, "FIREBASE_WEB_APP_ID", "FIREBASE_WEB_APP_ID"),
  measurementId: pickEnv(
    rootEnv,
    "FIREBASE_WEB_MEASUREMENT_ID",
    "FIREBASE_WEB_MEASUREMENT_ID",
  ),
  vapidKey: pickEnv(rootEnv, "FIREBASE_WEB_VAPID_KEY", "FIREBASE_WEB_VAPID_KEY"),
};

fs.writeFileSync(
  path.join(envDir, "firebase-config.generated.ts"),
  `/* Archivo generado por scripts/sync-from-root-env.cjs — no editar a mano. */
export const firebaseWebConfig = ${JSON.stringify(fbConfig, null, 2)} as const;
`,
  "utf8",
);

const swDir = path.join(frontendDir, "public", "firebase-cloud-messaging-push-scope");
fs.mkdirSync(swDir, { recursive: true });
const swConfig = {
  apiKey: fbConfig.apiKey,
  authDomain: fbConfig.authDomain,
  projectId: fbConfig.projectId,
  storageBucket: fbConfig.storageBucket,
  messagingSenderId: fbConfig.messagingSenderId,
  appId: fbConfig.appId,
  measurementId: fbConfig.measurementId || undefined,
};
fs.writeFileSync(
  path.join(swDir, "firebase-messaging-sw.js"),
  `// firebase-messaging-sw.js — generado por scripts/sync-from-root-env.cjs (no editar a mano).
importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging-compat.js');

const firebaseConfig = ${JSON.stringify(swConfig, null, 2)};

if (firebaseConfig.apiKey && firebaseConfig.appId) {
  firebase.initializeApp(firebaseConfig);
  const messaging = firebase.messaging();

  function resolveUrl(data) {
    const portal = data && data.portal ? String(data.portal) : '';
    if (portal === 'taller') {
      return '/taller/panel/emergencias/solicitudes';
    }
    if (portal === 'admin') {
      return '/admin/panel';
    }
    return '/';
  }

  messaging.onBackgroundMessage((payload) => {
    const notificationTitle = payload.notification?.title || 'EmergenciasViales';
    const notificationOptions = {
      body: payload.notification?.body || '',
      icon: '/assets/icons/icon-192x192.png',
      badge: '/assets/icons/icon-72x72.png',
      tag: (payload.data && payload.data.tipo) || 'general',
      data: payload.data || {},
    };
    return self.registration.showNotification(notificationTitle, notificationOptions);
  });

  self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const targetPath = resolveUrl(event.notification.data);
    const targetUrl = new URL(targetPath, self.location.origin).href;

    event.waitUntil(
      clients
        .matchAll({ type: 'window', includeUncontrolled: true })
        .then((windowClients) => {
          for (const client of windowClients) {
            if (client.url.startsWith(self.location.origin) && 'focus' in client) {
              client.navigate(targetUrl);
              return client.focus();
            }
          }
          return clients.openWindow(targetUrl);
        }),
    );
  });
}
`,
  "utf8",
);

console.log("[sync-from-root-env] mailhog + firebase config + messaging SW generados.");
