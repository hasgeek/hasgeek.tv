(function() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('/service-worker.js')
      .then(function(registration) {
        console.log('Service Worker registration successful with scope: ',
        registration.scope);
      })
      .catch(function(err) {
        console.log('Service Worker registration failed: ', err);
      });
    });

    // Setup a listener to track Add to Homescreen events.
    window.addEventListener('beforeinstallprompt', event => {
      event.userChoice.then(choice => {
        if (window.ga) {
          window.ga('send', 'event', 'Add to Home', choice.outcome);
        }
      });
    });
  }
})();
