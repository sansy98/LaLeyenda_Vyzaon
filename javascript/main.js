$(document).ready(function() {
        setTimeout(function(){
          $('header').remove();
        }, 7100)
});
$(document).ready(function() {
  setTimeout(function(){
    var element = document.getElementById("disable");
    element.classList.remove("f-scroll")
  }, 6000)
});
$(document).ready(function() {
    setTimeout(function(){
      var element = document.getElementById("loadingwindow");
      element.classList.add("animate__hinge")
    }, 6000)
  });
$(document).ready(function() {
    setTimeout(function(){
      var element = document.getElementById("display-window");
      element.classList.remove("visivle")
    }, 1000)
});