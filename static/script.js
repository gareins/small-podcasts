window.onload = function() {
    var input = document.getElementById('rss-url');
    var output = document.getElementById('generated-link');

    input.addEventListener('keyup', function(e){
        if(e.keyCode == 13)
            output.innerHTML = "heoh!";
    });
};
