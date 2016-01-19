$(document).ready(function(){
  function onLinkInputChange() {
    txt = $(this).val();
    console.log(txt);
    btn = $("#generate-button")

    if (txt.length == 0) {
      btn.attr("background", "#ccc");
    } else {
      btn.removeAttr("background");
    }
  }

  $("#feedUrlInput").on("input", onLinkInputChange);

  function init() {
    onLinkInputChange();
  }

  init();
});
