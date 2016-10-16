
app.directive('comment', function(){
    return {
        restrict: 'E',
        templateUrl: '/static/templates/comment.html',
        replace: true,
        scope: {
            data: '='
        },
        controller: function($scope, postService){

            $scope.is_rtl = utils.is_hebrew($scope.data.text);
            $scope.time_ago = utils.time_ago_str($scope.data.seconds_passed);

        },
        link: function(scope, el, attrs) {

        }
    };
});