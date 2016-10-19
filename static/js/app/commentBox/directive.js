
app.directive('commentBox', function(){
    return {
        restrict: 'E',
        templateUrl: '/static/templates/commentBox.html',
        replace: true,
        scope: {
            commentType: '@',
            data: '=',
            addCommentMethod: '&'
        },
        controller: function($scope, postService){

            $scope.comments = [];
            $scope.render_comments = function(page_n){

                if (typeof page_n == 'undefined')
                    page_n = 1;

                //comment_on, obj_id, p
                postService.get_comments({
                    comment_on: $scope.commentType,
                    obj_id: $scope.data.post_id,
                    p: page_n
                })
                .then(function(res){
                    if (res.success) {
                        $scope.comments = $scope.comments.concat(res.comments);
                    }
                    else utils.error('Error performing action: ' + res.error || 'Internal error');
                });

            };

        },
        link: function(scope, el, attrs) {

            $(el).find('.txt_add_comment').keyup(function(e){
                if (e.keyCode == 13) { // enter key
                    scope.addCommentMethod({
                        text: $(this).val(), 
                        post: scope.data
                    });
                }
            });

            scope.render_comments();
        }
    };
});