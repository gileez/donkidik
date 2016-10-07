
app.factory('postService', function($http){

    return {

        create_post: function(data){
            return utils.http.request($http, 'post', '/api/post/create', data);
        },

        delete_post: function(data){
            return utils.http.request($http, 'post', '/api/post/delete', data);
        },

        update_post: function(data){
            return utils.http.request($http, 'post', '/api/post/update', data);
        },

        comment_on_post: function(data){
            return utils.http.request($http, 'post', '/api/post/comment', data);
        },

        delete_comment: function(data){
            // todo
        },

        upvote: function(data){
            return utils.http.request($http, 'post', '/api/post/upvote', data);
        },

        downvote: function(data){
            return utils.http.request($http, 'post', '/api/post/downvote', data);
        },

    };
});