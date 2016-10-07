
app.factory('homeService', function($http){

    return {

        get_feed: function(){
            return utils.http.request($http, 'get', '/api/feed');
        },

    };
});