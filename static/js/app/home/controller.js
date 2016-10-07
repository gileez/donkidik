
app.controller('HomeController', function($scope, homeService){

    $scope.feed = [];
    $scope.feed_error = null;

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

    $scope.get_feed();

});