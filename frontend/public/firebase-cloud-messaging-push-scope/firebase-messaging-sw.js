// firebase-messaging-sw.js — generado por scripts/sync-from-root-env.cjs (no editar a mano).
importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging-compat.js');

const firebaseConfig = {
  "apiKey": "AIzaSyBh8dMiDzV7E1-mIX-trNolyso9Wq0A5T4",
  "authDomain": "transporte-si2.firebaseapp.com",
  "projectId": "transporte-si2",
  "storageBucket": "transporte-si2.firebasestorage.app",
  "messagingSenderId": "543278137943",
  "appId": "1:543278137943:web:XXXXXXXXXXXXXXXX"
};

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
