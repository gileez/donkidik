
app.factory('postService', function($http){

    function _get(url, data) {
        return utils.http.request($http, 'get', url, data);
    };

    function _post(url, data) {
        return utils.http.request($http, 'post', url, data);
    };

    return {

        create_post: function(data){
            return _post('/api/post/create', data);
        },

        delete_post: function(data){
            return _post('/api/post/delete', data);
        },

        update_post: function(data){
            return _post('/api/post/update', data);
        },

        get_comments: function(data){
            return _get('/api/comments', data);
        },

        add_comment: function(data){
            return _post('/api/comment/add', data);
        },

        delete_comment: function(data){
            // todo
        },

        upvote: function(data){
            return _post('/api/post/upvote', data);
        },

        downvote: function(data){
            return _post('/api/post/downvote', data);
        },

    };
});