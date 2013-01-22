var newImageOpacity = 0.00;
var timer = new Array();
var facebook_app_id = '416260668426967';

// Iterates the imgsArray to cicle the frontImage(Div) and backImage(Div) correctly. THE DIVS CAME FROM THE TEMPLATE
// TODO SHOULD RECEIVE fof_index. 
function homefade(backImgDiv, frontImgDiv, fof_index, backImageIndex, frontImageIndex) {
	if (frames[fof_index].length > 1) {
		if (!backImageIndex && !frontImageIndex) {
			var backImageIndex = 0;
			var frontImageIndex = 1;
		}
		// Loop:
		if (frontImageIndex == (frames[fof_index].length - 1)) {
			frontImageIndex = 0;
			backImageIndex = frames[fof_index].length - 1;
		} else {    
			frontImageIndex++;
			// Loop:
			if (backImageIndex == (frames[fof_index].length - 1)) {
				backImageIndex = 0;
			} else {
				backImageIndex++;
			}
		}

		if (!backImageDiv || !frontImageDiv) {
			var backImageDiv = document.getElementById(backImgDiv);
			var frontImageDiv = document.getElementById(frontImgDiv);
		}
		
		frames[fof_index][backImageIndex].class = "backImage";
		frames[fof_index][frontImageIndex].class = "frontImage";
		frames[fof_index][backImageIndex].style.opacity= "1";
		
		//Adds the back Image object:
		if (backImageDiv.hasChildNodes()) {
			 backImageDiv.removeChild(backImageDiv.lastChild);
		 }      
		backImageDiv.appendChild(frames[fof_index][backImageIndex]);
		
		
		//Hides the front image:
		frames[fof_index][frontImageIndex].style.opacity= "0";
		//Adds front image object:
		if (frontImageDiv.hasChildNodes()) {
			frontImageDiv.removeChild(frontImageDiv.lastChild);
		}
		frontImageDiv.appendChild(frames[fof_index][frontImageIndex]);
		timer[fof_index] = setInterval(function(){homefadeTrans(backImgDiv, frontImgDiv, fof_index, backImageIndex, frontImageIndex);}, 10);
		
	} else {
		var backImageDiv = document.getElementById(backImgDiv);
		frames[fof_index][0].id = "backImage";
		frames[fof_index][0].style.opacity = "1";
		backImageDiv.appendChild(frames[fof_index][0]);
	}
}

// Fades the pictures frontImage and backImage so when one of the pics reaches 100%, it calls the homefade function
function homefadeTrans(backImgDiv, frontImgDiv, fof_index, backImgIndex, frontImgIndex) {
    if (newImageOpacity >= 100.0) {
        clearTimeout(timer[fof_index]);
        timer[fof_index] = 0;
        if (fof_index == 0) {
	        newImageOpacity = 0;
        }
        
        setTimeout(function(){homefade(backImgDiv, frontImgDiv, fof_index, backImgIndex, frontImgIndex);}, 2000);   
    } else {
        frames[fof_index][frontImgIndex].style.opacity = newImageOpacity/100.0;
        frames[fof_index][frontImgIndex].style.filter = "alpha(opacity="+newImageOpacity+")";
        if (fof_index == 0) {
	        newImageOpacity = newImageOpacity + 1;
        }        
    }
}

function appendFof(fof_index){
	var div1 = $('<div class="colwrap_fof"></div>');   		//THE DIV ITSELF
	
		/*  ATTRIBUTES OF THE SHARE BUTTON:*/
	if(fof_index != 0){
		$("#df_background").append($('<hr />'));	
	}
	$("#df_background").append(div1);
	
	var div2 = $('<div class="homeimg"></div>');				//THE FOFs
	var div21 = $('<div id="backImageDiv'+fof_index+'" class="backDiv"></div>');
	var div22 = $('<div id="frontImageDiv'+fof_index+'"  class="frontDiv"></div>');
	div2.append(div21);
	div2.append(div22);
	div1.append(div2);

	var div3 = $('<div class="all_buttons"></div>');			//THE BUTTONS BELLOW THE FOF
	var div31 = $('<div class="fb_buttons"></div>');
	var div311 = $('<div class="share"></div>');
	var div3111 = $('<img src = "'+static_url+'images/share_facebook.png" id="share_button'+fof_index+'" class="btn_share" type="button_count">');
	var div312 = $('<div class="fb-like" data-href="https://dyfoc.us/uploader/'+fof_names[fof_index]+'/share_fof/" data-send="false" data-layout="button_count" data-width="450" data-show-faces="true" data-font="arial"></div>');
	div3.append(div31.append(div311.append(div3111)).append(div312));
	
	var div32 = $('<div class="embed_counter"></div>');
	var div321 = $('<div class="accordion" id="accordion'+fof_index+'"></div>');
	var div3211 = $('<div class="accordion-heading"></div>');
	var div32111 = $('<a class = "btn btn-small btn-link" data-toggle="collapse" data-parent="#accordion'+fof_index+'" href="#collapse'+fof_index+'"> Embed </a>');
	div32.append(div321.append(div3211.append(div32111)))

	var div322 = $('<div class="fof_views">'+ fof_views[fof_index] +' views</div>');
	div32.append(div322);
	
	div3.append(div32);
	div1.append(div3);
	
	var div4 = $('<div id="collapse'+fof_index+'" class="accordion-body collapse"></div>');	//THE FRAME THAT WILL SHOW OR HIDE (EHEN CLICKING THE EMBED BTN)
	var div41 = $('<div class="accordion-inner"></div>');
	var div411 = $('<form class="well form-inline"></form>');
	var div4111 = $('<h4><i>Copy and paste the following code into your website:</i></h4>');
	var div4112 = $('<textarea id="textEmbed'+fof_index+'" style="width:500px" name="embedded_link" rows="3"></textarea>');
	var div4113 = $('<h4> Change size: </h4>');
	var div41131 = $('<input title="Height" id="fofHeight'+fof_index+'" style="width: 50px;" type="text" class="span3" placeholder="Height"> x </input>');
	var div41132 = $('<input title="Width" id="fofWidth'+fof_index+'" style="width: 50px;" type="text" class="span3 disabled" placeholder="Width" disabled>    </input>');
	var div41133 = $('<button type="button" class="btn btn-inverse" id="btnResize'+fof_index+'">Resize</button>');
	div4113.append(div41131).append(div41132).append(div41133);
	div411.append(div4111).append(div4112).append(div4113);
	div4.append(div41.append(div411));
	div1.append(div4);
	
	var div5 = $('<div class="posted_by"> <b>Posted by </b>'+fof_users[fof_index] +'<b> on </b>'+ fof_pub_dates[fof_index]+'</div>');  // POSTED BY...
	div1.append(div5);
	
	timer[fof_index] = 0;
	homefade("backImageDiv"+fof_index, "frontImageDiv"+fof_index, fof_index);
	resize('textEmbed'+fof_index, 'fofWidth'+fof_index, 'fofHeight'+fof_index, fof_index);
	customize_buttons(fof_index);
}

//TODO Should receive the ids of fofWidth, fofHeight and btnResize
function after_loading(){
	$(window).bind("load", function() {
		bodyScript();
		appendFof(0);
	});
}

function customize_buttons(fof_index){
	$(document).ready(function(){
		$('#btnResize'+fof_index).click(function(){
			resize('textEmbed'+fof_index, 'fofWidth'+fof_index, 'fofHeight'+fof_index, fof_index);});
		$('#share_button'+fof_index).click(function(e){
			e.preventDefault();	
			FB.ui(
			{
				method: 'feed',
				name: fof_users[fof_index]+"'s FOF",
				link: "https://dyfoc.us/uploader/"+fof_names[fof_index]+"/share_fof/",
				picture: frames[fof_index][0].src,
				caption: window.location.href,
				description: "This FOF was taken by "+ fof_users[fof_index],
				message: ''
			});		
		});
	});		
}

function resize(embed_link, fofWidth, fofHeight, fof_index) {
	var height = $('#'+fofHeight);
	
	if (height.val() == ""){
		height.val("576");
	}
	var pic = frames[fof_index][0];
	var widthFactor = (pic.width)/(pic.height);
	
	var width = height.val()*widthFactor;	
	width = width.toFixed(0);
	$('#'+fofWidth).val(width);
	
	var myvar = "<iframe src= 'http://dyfoc.us/uploader/"+fof_names[fof_index]+
		"/embedded_fof/"+height.val()+"/height/' width="+width+" height="+height.val()+" frameborder='no' "+
		"scrolling='no' marginwidth='0' marginheight='0' vspace='0' hspace='0'></iframe>";
	$('#'+embed_link).val(myvar);
}

function headScript(mobileAddress) {
/*  CHANGE THE PAGE IN CASE OF IPHONE OR IPAD	*/
	if ((navigator.userAgent.match(/iPhone/i)) || (navigator.userAgent.match(/iPod/i))) {
   		location.replace(mobileAddress);
	}
	
	/*  GOOGLE ANALYTICS:*/	
	var _gaq = _gaq || [];
	_gaq.push(['_setAccount', 'UA-35287341-1']);
	_gaq.push(['_trackPageview']);

	(function() {
		var ga = document.createElement('script'); 
		ga.type = 'text/javascript'; 
		ga.async = true;
		ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
		var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	})();
	
	// FUNCTIONS TO BE CALLED AFTER LOADING
	after_loading();
}

function bodyScript(){
	/*  FACEBOOK CONNECTION (USED FOR GLOBAL LIKE BUTTON):  */
	window.fbAsyncInit = function() {
		FB.init({appId: facebook_app_id, status: true, cookie: true, xfbml: true});
	};
	(function() {
		var e = document.createElement('script'); 
		e.async = true;
		e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
		document.getElementById('fb-root').appendChild(e);
	}());
}
