function fade(element) {
    var op = 1;  // initial opacity
    var timer = setInterval(function () {
        if (op <= 0.1){
            clearInterval(timer);
            element.style.display = 'none';
        }
        element.style.opacity = op;
        element.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op -= op * 0.03;
    }, 100);
}

function buy(name,storage,id) {
  var xmlhttp = new XMLHttpRequest();
  var url = '/buyProduct/' + name + '/' + storage;
  //alert(url);
  xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4) {
      //document.getElementById('').innerHTML = 'Congratulations!';
      msg = document.getElementById(id);
      msg.innerHTML = "<center>Congratulations! Transaction successfull :D</center>";
      msg.style.color = 'green';
      fade(document.getElementById(id+'p'));
    }
  }
  xmlhttp.open("GET",url, true);
  xmlhttp.send();

}
