var a,b;
function f1()
{
a=document.getElementById("ap_password").value;
b=document.getElementById("ap_confirmPass").value;
if(a!=b)
{alert("password and confirm password doesn't match");
	document.getElementById("ap_confirmPass").focus();
	return false;
}
}