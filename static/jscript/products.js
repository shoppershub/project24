function GetValues(productClass) {
  //alert(data.getElementsByClassName('productName')[0].innerHTML);
  //alert(productClass.getElementsByClassName('productStorage')[0].innerHTML);
  var getname = productClass.getElementsByClassName('productName')[0].innerHTML;
  var getsize = productClass.getElementsByClassName('productStorage')[0].innerHTML;
  var size = getsize.trim();
  var name = getname.trim();
  var href = "/productInfo/" + name + "/" + size;
  window.location.href = href;
}

function showHint(str) {
  if(str.length == 0) {
    document.getElementById('hintBox').style.display = 'none';
    document.getElementById('txtHint').innerHTML = "";
    return;
  }
  else {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var txtHint = JSON.parse(this.responseText);
        var display = "";
        for (var i = 0; i < txtHint.length; i++) {
          display += "<li id ='hint' onclick='writeHint(this.innerHTML)'>" + txtHint[i].name + "</li>";
        }
        document.getElementById('hintBox').style.display = 'block';
        document.getElementById('txtHint').innerHTML = display;
      }
    };
    xmlhttp.open("GET",'/search?q=' + str, true);
    xmlhttp.send();
  }
}

function writeHint(hint) {
  document.getElementsByName('searchbox')[0].value = hint;
}
function getValuesForCart(){
  var productClass=document.getElementsByClassName('product');
  var getname = productClass.getElementsByClassName('productName')[0].innerHTML;
  var getsize = productClass.getElementsByClassName('productStorage')[0].innerHTML;
  var size = getsize.trim();
  var name = getname.trim();
  var href = "/Cart/" + name + "/" + size;
  window.location.href = href;
}
