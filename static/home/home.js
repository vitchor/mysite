// jQuery part:

$(document).ready(function(){
    $('#login').click(function(){
        logMeIn();
    });
    $('#description').hide();
    $('#description-collapser').click(function(){
        $('#description').slideToggle('fast');
    });
});

// JS part:
window.fbAsyncInit = function() {
// init the FB JS SDK
FB.init({
  appId      : '417476174956036', // App ID from the App Dashboard
  channelUrl : '/static/home/channel.html', // Channel File for x-domain communication
  status     : true, // check the login status upon init?
  cookie     : true, // set sessions cookies to allow your server to access the session?
  xfbml      : true  // parse XFBML tags on this page?
});

// Additional initialization code such as adding Event Listeners goes here

FB.getLoginStatus(function(response) {
  if (response.status === 'connected') {
    // connected
    FB.api('/me?fields=name,id,email', function(response) {
        // Remove the next comment to automatically redirect to user feed:
        //location.replace('http://dyfoc.us/uploader/'+response.id+'/feed/0/');
        $('#login').text('');
        $('#welcome').text('Welcome, ');
        $('#username').text(response.name+' (');
        $('#logout').text('logout');
        $('#logout').click(function(){
           FB.logout(function(response){
               top.location.href = "http://dyfoc.us/";
           });
        });
        $('#point').text('). ');
        $('#view-feed').text('View feed >');
        $('#view-feed').attr('href','http://dyfoc.us/uploader/'+response.id+'/feed/0/');
        $.post('/uploader/user_web_info/', {
            name: response.name,
            facebook_id: response.id,
            email: response.email
        },
            function(data) {
                //alert(data);
            }
        );

    });
  } else if (response.status === 'not_authorized') {
    // not_authorized
    //login();
    $('#username').text('');
    $('#login').text('Connect with Facebook');
  } else {
    // not_logged_in
    //login();
    $('#username').text('');
    $('#login').text('Log in or Sign Up');
  }
 });

};

function login() {
  FB.login(function(response) {
      if (response.authResponse) {
          // connected
          testAPI();
      } else {
          // cancelled
      }
  });
}

function logMeIn() {
  var paramsLocation=window.location.toString().indexOf('?');
  var params="";
  if (paramsLocation>=0) params=window.location.toString().slice(paramsLocation);
  top.location = 'https://graph.facebook.com/oauth/authorize?client_id=417476174956036&scope=email&redirect_uri=http://dyfoc.us'+params;
}

// Load the SDK's source Asynchronously
// Note that the debug version is being actively developed and might 
// contain some type checks that are overly strict. 
// Please report such bugs using the bugs tool.
(function(d, debug){
     var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
     if (d.getElementById(id)) {return;}
     js = d.createElement('script'); js.id = id; js.async = true;
     js.src = "//connect.facebook.net/en_US/all" + (debug ? "/debug" : "") + ".js";
     ref.parentNode.insertBefore(js, ref);
}(document, /*debug*/ false));