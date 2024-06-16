$(document).ready(function(){
    $("#hide_ua").click(function(){
      $("#unapproved").toggle();
    });
  });

  $(document).ready(function(){
    $("#hide_a").click(function(){
      $("#approved").toggle();
    });
  });

window.addEventListener('beforeunload', function (e) {
    navigator.sendBeacon('/logout');
});
