(function(){
    function _http_is_success(response){
        return (response.data.status && response.data.status == 'OK');
    };

    function _http_return(is_success, extra_data){
        if (typeof extra_data == 'undefined')
            extra_data = {};

        extra_data.success = is_success;
        return extra_data;
    };

    function _http_return_success(extra_data){
        return _http_return(true, extra_data);
    };

    function _http_return_fail(extra_data){
        return _http_return(false, extra_data);
    };

    function _service_result(result){
        var ret_func = _http_is_success(result) ?
            _http_return_success : 
            _http_return_fail;

        return ret_func(result.data);
    };

    var utils = {

        http: {
            request: function($http, method, url, data){
                if (typeof data == 'undefined')
                    data = {};

                method = method.toLowerCase();
                if (method == 'get') {
                    var qs = '';
                    for (var key in data)
                        qs += key + '=' + data[key] + '&';
                    if (url.indexOf('?') != -1)
                        url = url + '&' + qs;
                    else
                        url = url + '?' + qs;
                }
                return $http[method](url, data)
                .then(function(res){
                    return _service_result(res);
                })
                .catch(function(res){
                    return _service_result(res);
                });                
            }
        },

        error: function(message){
            alert(message);
        },

        is_hebrew: function(text){
            return (text && text.match(/[\u0590-\u05FF]/) != null);
        },

        time_ago_str: function(seconds){
            var interval = Math.floor(seconds / 31536000);
            if (interval >= 1) {
                if (interval == 1)
                    return 'a year';
                return interval + " years";
            }
            interval = Math.floor(seconds / 2592000);
            if (interval >= 1) {
                if (interval == 1)
                    return 'a month';
                return interval + " months";
            }
            interval = Math.floor(seconds / 604800);
            if (interval >= 1) {
                if (interval == 1)
                    return 'a week';
                return interval + " weeks";
            }
            interval = Math.floor(seconds / 86400);
            if (interval >= 1) {
                if (interval == 1)
                    return 'a day';
                return interval + " days";
            }
            interval = Math.floor(seconds / 3600);
            if (interval >= 1) {
                if (interval == 1)
                    return 'an hour';
                return interval + " hours";
            }
            interval = Math.floor(seconds / 60);
            if (interval >= 1) {
                if (interval == 1)
                    return 'a minute';
                return interval + " minutes";
            }
            if (Math.floor(seconds) <= 1) {
                return 'a second';
            }

            return Math.floor(seconds) + " seconds";
        },
    };

    window.utils = utils;
})();