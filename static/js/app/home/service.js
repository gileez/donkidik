
app.factory('homeService', function($http){

    function _get(url, data) {
        return utils.http.request($http, 'get', url, data);
    };

    return {

        get_feed: function(page_n){

            if (typeof page_n == 'undefined')
                page_n = 1;

            return _get('/api/feed', {p: page_n});
        },

        get_sessions: function(){
            return _get('/api/sessions');
        },

    };
});