function runSlide(n){
	showSlide(slideindex+=n);
}
function showSlide(n){
	var i;
	var slides=document.getElementsByClassName("slide");
	if(n>slides.length)
		slideindex=1;
	if(n<1)
		slideindex=slides.length;
	for(i=0; i<slides.length; i++){
		slides[i].style.display="none";
	}
	slides[slideindex-1].style.display="block";
}
function calctime(distance){
	var now=new Date().getTime();
	var distance=countdowndate-now;
	var dd,hh,mm,ss;
	dd=Math.floor(distance/(1000*60*60*24));
	hh=Math.floor((distance%(1000*60*60*24))/(1000*60*60));
	mm=Math.floor((distance%(1000*60*60))/(1000*60));
	ss=Math.floor((distance%(1000*60))/(1000));
	
	document.getElementById("time").innerHTML=dd+"days, "+hh+"hours, "+mm+"minutes, "+ss+"seconds left";
	if(distance<0){
		clearInterval(x);
		document.getElementById("time").innerHTML="Expired";
	}
}