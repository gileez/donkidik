(function(){
  var app = angular.module('donkidik', ['ngSanitize']);

  app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  });

  app.config(['$httpProvider', function ($httpProvider) {
    // intercept posts requests, convert to standard form encoding
    $httpProvider.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
    $httpProvider.defaults.transformRequest.unshift(function (data, headersGetter) {
      var key, result = [];
      for (key in data) {
        if (data.hasOwnProperty(key)) {
          result.push(encodeURIComponent(key) + "=" + encodeURIComponent(data[key]));
        }
      }
      return result.join("&");
    });
  }]);

  app.filter('newline', function () {
    return function(text) {
      return text.replace(/\n/g, '<br/>');
    };
  });

  // app.filter('trusted', ['$sce', function ($sce) {
  //   return function(url) {
  //     return $sce.trustAsResourceUrl(url);
  //   };
  // }]);

  window.app = app;
})();