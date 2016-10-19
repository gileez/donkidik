
app.directive('post', function(postService){
    return {
        restrict: 'E',
        templateUrl: '/static/templates/post.html',
        replace: true,
        scope: {
            data: '='
        },
        controller: function($scope){

            $scope.is_rtl = utils.is_hebrew($scope.data.text);
            $scope.time_ago = utils.time_ago_str($scope.data.seconds_passed);
            $scope.show_media = false;

            $scope.upvote = function(post){
                postService.upvote(post)
                .then(function(res){
                    if (res.success) {
                        $scope.data.is_downvoted = false;
                        $scope.data.is_upvoted = !$scope.data.is_upvoted;
                        $scope.data.post_score = res.updated_score;
                    }
                    else utils.error('Error performing action: ' + res.error || 'Internal error');
                });
            };

            $scope.downvote = function(post){
                postService.downvote(post)
                .then(function(res){
                    if (res.success) {
                        $scope.data.is_upvoted = false;
                        $scope.data.is_downvoted = !$scope.data.is_downvoted;
                        $scope.data.post_score = res.updated_score;
                    }
                    else utils.error('Error performing action: ' + res.error || 'Internal error');
                });
            };

            $scope.add_comment = function(text, post){
                if (!text)
                    return;

                var data = {
                    comment_on: 'post',
                    obj_id: post.post_id,
                    text: text
                };
                
                postService.add_comment(data)
                .then(function(res){
                    if (res.success) {
                        $scope.new_comment_text = '';
                        postService.get_comments(data)
                        .then(function(res){
                            if (res.success) {
                                $scope.data.comments = res.comments;
                            }
                            else utils.error('Error performing action: ' + res.error || 'Internal error');
                        });
                    }
                    else utils.error('Error performing action: ' + res.error || 'Internal error');
                });
            };
        },
        link: function(scope, el, attrs) {

        }
    };
});