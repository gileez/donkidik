
app.controller('HomeController', function($scope, homeService, postService){

    $scope.feed = [];
    $scope.feed_error = null;
    $scope.sessions = [];
    $scope.sessions_error = null;

    $scope.get_feed = function(){
        homeService.get_feed()
        .then(function(res){
            if (res.success){
                $scope.feed = res.posts;
            }
            else {
                $scope.feed_error = res.error || 'Error';
            }
        });
    };


    $scope.get_sessions = function(){
        homeService.get_sessions()
        .then(function(res){
            if (res.success){
                $scope.sessions = res.sessions;
            }
            else {
                $scope.sessions_error = res.error || 'Error';
            }
        });
    };
    /***/
    // MOVE THESE TO THE POST DIRECTIVE
    /***/
    $scope.upvote = function(post){
        postService.upvote({post_id: post.post_id})
        .then(function(res){
            console.log(res);
        });
    };
    $scope.downvote = function(post){
        postService.downvote({post_id: post.post_id})
        .then(function(res){
            console.log(res);
        });
    };
    $scope.delete = function(post){
        postService.delete_post({post_id: post.post_id})
        .then(function(res){
            console.log(res);
        });
    };

    $scope.get_feed();
    $scope.get_sessions();

});