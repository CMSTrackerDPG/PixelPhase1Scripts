var PixelTrackerShow = {} ;
PixelTrackerShow.thisFile = "my.js";

var interestingQuantities = ["FEDID", "FEDposition", "FEDchannel"]

PixelTrackerShow.init = function()
{
  showData = PixelTrackerShow.showData;  
}

PixelTrackerShow.showData = function (evt) 
{
  var myPoly = evt.currentTarget;
  
  if (evt.type == "mouseover") 
  {
    var myPoly = evt.currentTarget;
    var id = myPoly.getAttribute("detId");
    var oid = myPoly.getAttribute("oid");
    var fedChannel = myPoly.getAttribute("FEDchannel");

    var textfield = document.getElementById("moduleName");
    textfield.firstChild.nodeValue = oid + " (" + id + ")";
    
    for (var i = 0; i < interestingQuantities.length; ++i)
    {
      var k = interestingQuantities[i];
      var s = myPoly.getAttribute(k);
      
      if (s == null) s = ""; // Id not found in cabling DB
      
      var nk = k + "_val";
      document.getElementById(nk).innerHTML = s;
    } 
  }
  ShowTooltip(evt);
  
  if (evt.type == "mouseout") 
  {  
    HideTooltip();
  }
}

function ShowTooltip(evt)
{
  var tooltip_bg = document.getElementById('tooltip_bg');
  var infoTable = document.getElementById('infoTable');
  
  var winWidth = window.innerWidth;
  var winHeight = window.innerHeight;
  
  var tooltipX = evt.pageX + 3;
  var tooltipY = evt.pageY;
  
  var tooltipWidth = 350;//document.getElementById('line1').getComputedTextLength();
  var tooltipHeight = 100;
  
  // make tooltip fit into its parent
  if (tooltipX + tooltipWidth >= winWidth)
  {
    tooltipX = evt.pageX - 3 - tooltipWidth;
  }
  if (tooltipY + tooltipHeight >= winHeight)
  {
    tooltipY = evt.pageY - tooltipHeight + 20
  }  
  
  tooltip_bg.setAttributeNS(null,"x",tooltipX);
	tooltip_bg.setAttributeNS(null,"y",tooltipY);
	tooltip_bg.setAttributeNS(null,"visibility","visible");
  tooltip_bg.setAttributeNS(null,"width",tooltipWidth);
  
  infoTable.setAttributeNS(null,"x",tooltipX);
	infoTable.setAttributeNS(null,"y",tooltipY);
	infoTable.setAttributeNS(null,"visibility","visible");
}
function HideTooltip()
{
  document.getElementById('tooltip_bg').setAttributeNS(null,"visibility","hidden");
  document.getElementById('infoTable').setAttributeNS(null,"visibility","hidden");
}
