
app.factory('homeService', function($http){

    function _get(url) {
        return utils.http.request($http, 'get', url);
    };

    return {

        get_feed: function(){
            return _get('/api/feed');
        },

        get_sessions: function(){
            return _get('/api/sessions');
        },

    };
});