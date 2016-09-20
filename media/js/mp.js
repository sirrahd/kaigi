angular.module('MeetingPulse', ['n3-line-chart'])
.config(function($httpProvider, $interpolateProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
    $httpProvider.defaults.headers.put['Content-Type'] = 'application/x-www-form-urlencoded';
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
})
.controller('MeetingController', ['$scope', '$http', function($scope, $http) {
    $scope.meetingList = [];
    $scope.loaded = false;

    getEvents();

    function getEvents() {
        $http.get('/events/')
        .success(function(data) {
            $scope.meetingList = data.events;
            $scope.loaded = true;
        })
        .error(function(data) {
            window.location='/auth';
        });
    };
}])
.factory('Constants', function(DjangoConstants) {
    var constants = {
    };
    angular.extend(constants, DjangoConstants);

    return {
        get: function(key) {
            return constants[key];
        },
        all: function() {
            return constants;
        }
    };
})
.directive('schrollBottom', function () {
    return {
        scope: {
            schrollBottom: "="
        },
        link: function (scope, element) {
            scope.$watchCollection('schrollBottom', function (newValue) {
                if (newValue)
                {
                    $(element).scrollTop($(element)[0].scrollHeight);
                }
            });
        }
    }
})
.controller('MeetingPulseController', ['$scope', '$http', '$timeout', 'Constants', function($scope, $http, $timeout, Constants) {
    $scope.meeting_id = Constants.all()['meeting_id'];
    $scope.chats = [];
    $scope.ratings = [];
    $scope.meeting = {};
    $scope.last_rating = 0;
    $scope.last_chat = 0;
    $scope.message = "";
    $scope.rating = 100;
    $scope.rolling_ratings = [];
    $scope.lineData = [];
    $scope.lineOptions = {
        axes: {
            x: {key: 'x', type: 'linear', min: 0, max: 300, ticks: 0},
            y: {type: 'linear', min: 0, max: 100, ticks: 0},
        },
        series: [
            {y: 'value', color: 'steelblue', thickness: '2px', type: 'area', striped: true},
        ],
        tooltip: {mode: 'none' },
        lineMode: 'linear',
        tension: 0.7,
        drawLegend: false,
        drawDots: false,
        hideOverflow: false,
        columnsHGap: 5
    }

    getUpdate();

    function getUpdate() {
        if ($scope.request_count) {
            return;
        }
        $http.get('/events/' + $scope.meeting_id + '/?last_chat=' + $scope.last_chat + '&last_rating=' + $scope.last_rating)
        .success(function(data) {
            processUpdate(data);
            $timeout(getUpdate, 2000);
        })
        .error(function(data) {
            $timeout(getUpdate, 30000);
        });
    };

    function processUpdate(data) {
        $scope.meeting = data.meeting;
        for (i = 0; i < data.chats.chats.length; i++) {
            addChat(data.chats.chats[i]);
        }
        for (i = 0; i < data.ratings.ratings.length; i++) {
            addRating(data.ratings.ratings[i]);
        }
        $scope.last_chat = data.chats.last_id;
        $scope.last_rating = data.ratings.last_id;
        $scope.rolling_ratings = data.rolling_ratings;
        prepareRating(data.current_rating);
        prepareLine();
    };

    function prepareRating(rating) {
        $scope.rating = rating;
        if (rating < 25) {
            $("#death").addClass('active');
            $('#ok').removeClass('active');
            $('#wow').removeClass('active');
        }
        else if (rating >= 25 && rating <= 75) {
            $("#death").removeClass('active');
            $("#ok").addClass('active');
            $("#wow").removeClass('active');
        }
        else {
            $("#death").removeClass('active');
            $("#ok").removeClass('active');
            $("#wow").addClass('active');
        }
    };

    function prepareLine() {
        $scope.lineData = [];
        for (i = 0; i < $scope.rolling_ratings.length; i++) {
            $scope.lineData.push({
                'x': $scope.rolling_ratings[i][0],
                'value': $scope.rolling_ratings[i][1],
            });
        }
    };

    function addRating(rating) {
        if (idInSet(rating.id, $scope.ratings)) {
            return;
        }
        $scope.ratings.push(rating);
    };

    function addChat(chat) {
        if (idInSet(chat.id, $scope.chats)) {
            return;
        }
        $scope.chats.push(chat);
    };

    $scope.postRating = function(rating) {
        $http.post('/events/' + $scope.meeting_id + '/rate/', 'last_chat=' + $scope.last_chat + '&last_rating=' + $scope.last_rating + '&rating=' + rating )
        .success(function(data) {
            processUpdate(data);
        })
    };

    $scope.postChat = function() {
        if ($scope.message === "" ) {
            return;
        }
$http.post('/events/' + $scope.meeting_id + '/chat/', 'last_chat=' + $scope.last_chat + '&last_rating=' + $scope.last_rating + '&message=' + encodeURIComponent($scope.message) )
        .success(function(data) {
            processUpdate(data);
            $scope.message = "";
        });
    };

    function idInSet(id, set) {
        for (i = 0; i < set.length; i++) {
            if (set[i].id == id) {
                return true;
            }
        }
        return false;
    };
}])

