function GetValues(productClass) {
  //alert(data.getElementsByClassName('productName')[0].innerHTML);
  var getname = productClass.getElementsByClassName('productName')[0].innerHTML;
  var name = getname.trim();
  var href = "/productInfo/" + name;
  window.location.href = href;
}

  /*var request = new XMLHttpRequest();
  request.open('POST', '/productInfo', true);

  request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
  request.send(name);
  /*if (request.status === 200) {
    request.abort();
    console.log(request.responseText);
  }
  //request.close()
  /*request.onload = function(){if (httpRequest.readyState === 2) {
    request.abort();
  }
}
  /*.done(funcion(result) {
    console.log(result)
  }*/
