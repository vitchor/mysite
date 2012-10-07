
var newImage;
var oldImage;

var newImageIndex = 0;

var newImageOpacity = 0.00;
var oldImageOpacity = 100.00;            

var timer = 0;

var homediv;

function homefade() {
    /*
    if (!homediv) {
        homediv = document.getElementById("homeimg");

    } else {
        
        
        if (newImage) {
            
            if (oldImage) {
                homediv.removeChild(oldImage);
            }
            
            oldImage = newImage;
        }
        
        newImage = document.createElement('img');
        newImage.src = imgsArray[newImageIndex];

        newImage.id = "fof_viewer_r3_c4"              
        newImage.style.opacity = "0";
        newImage.style.filter = "alpha(opacity=0)";
        //newImage.style.height = "auto";
        //newImage.style.width = "auto";

        //newImage.style.position = 'absolute';
        homediv.appendChild(newImage);
        if (oldImage) {
            newImage.style.position = 'absolute';
            var big_coordinates=getXYpos(oldImage);
            var bp_x = big_coordinates['x'];
            var bp_y = big_coordinates['y'];
            
            newImage.style.left = bp_x + 'px';
            newImage.style.top = bp_y + 'px';
        }
        
        if (newImageIndex == (imgsArray.length-1)) {
            newImageIndex = 0;
            
        } else {
            newImageIndex++;
        };
        
        timer = setInterval("homefadeTrans();", 1);
    }*/
}

function homefadeTrans() {
    if (newImageOpacity >= 100) {
        clearTimeout(timer);
        
        timer = 0;
        newImageOpacity = 0;
        oldImageOpacity = 100;

        setTimeout("homefade();", 1000);

    } else {

        newImage.style.opacity = newImageOpacity/100;
        newImage.style.filter = "alpha(opacity="+newImageOpacity+")";
        newImageOpacity = newImageOpacity+1;

        if (oldImage) {
            //oldImage.style.opacity = oldImageOpacity/100;
            //oldImage.style.filter = "alpha(opacity="+oldImageOpacity+")";
            //oldImageOpacity = oldImageOpacity-1;
        }
    }
}

function getXYpos(elem) {

   if (!elem) {
      return {"x":0,"y":0};
   }

   var xy = {"x":elem.offsetLeft,"y":elem.offsetTop}
   var par = getXYpos(elem.offsetParent);

   for (var key in par) {
      xy[key] += par[key];
   }

   return xy;
}