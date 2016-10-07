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
                return $http[method](url, data)
                .then(function(res){
                    return _service_result(res);
                })
                .catch(function(res){
                    return _service_result(res);
                });                
            },


        },

    };

    window.utils = utils;
})();