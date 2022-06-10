
  window.addEventListener( "pageshow", function ( event ) {
    var historyTraversal = event.persisted ||
                           ( typeof window.performance != "undefined" &&
                                window.performance.navigation.type === 2 );
    if ( historyTraversal ) {
      // Handle page restore.
      window.location.reload();
    }
  });

  $('form').submit(function(e) {
          e.preventDefault();
         var img_ele = document.getElementsByClassName("upload-image")
         var formData = new FormData(this);
         console.log("formdata catched file number : "+img_ele.length);
         if(img_ele.length==0){
           swal(
             {title: "Warning",
             text: '上傳照片不能為空',
             icon: "warning",
             type: 'warning',
           }).then((isConfirm) =>{
               if (isConfirm) {
                window.location.reload();
               }
           });
         }
         else{
           for (var i=0; i < img_ele.length; i++) {
             formData.append('images', img_ele.item(i).getAttribute("value"));
           }
           $('body').scrollTop(0);
            $("#progressId").show();
            $.ajax({
                xhr : function(){
                  var xhr = new window.XMLHttpRequest();
                  xhr.upload.addEventListener('progress',function(e){
                      if(e.lengthComputable){
                          var percent = Math.round((e.loaded / e.total)*50);
                          $("#progressbar").attr("aria-valuenow",percent*2).css("width",percent+"%").text(percent*2+"%");
                      }
                  });
                  return xhr;
                },
                url: "",
                type: 'POST',
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
                complete: function(xmlHttp) {
                  // xmlHttp is a XMLHttpRquest object
                  $('form').each(function(){
                      //this.reset();   //Here form fields will be cleared.
                  });
                  if (xmlHttp.status == 200) {
                    top.location.href = "/"+cur_lang+"/demo/inputdata";
                  }
                  else{
                    top.location.href = "/"+cur_lang+'/demo/';
                  }
                }
            });

         };


  });



  function convertFile(file) {
	        return new Promise((resolve,reject)=>{
			          let reader = new FileReader()
			          reader.readAsDataURL(file)
			          reader.onload = () => { resolve(reader.result) }
			          reader.onerror = () => { reject(reader.error) }
			      });
	    }


  var count = 0;
  $("input.input-file").change(function(e) {
	        console.log("input starting");
	        console.log("Table length : ",document.getElementById("POITable").rows.length)
	            var files = e.originalEvent.srcElement.files;

	            $.map(files, file =>convertFile(file).
			                then((data) =>{
						               insRow(URL.createObjectURL(file),data);
                           onDragListener("distanceRange"+(count-1),"textInput"+(count-1));
						            }));
	        $("input.input-file").val("");


	    });

    var arrHead = new Array();	// array for header.
    arrHead = ['id', 'image','type','del'];
    function deleteRow(row) {
        var i = row.parentNode.parentNode.rowIndex;
        document.getElementById('POITable').deleteRow(i);
    }

    function onDragListener(distanceRange,textInput){
      var slider = document.getElementById(distanceRange);
      var output = document.getElementById(textInput);
      slider.oninput=function(){
        output.innerHTML = this.value +" cm";
        output.value=this.value;
        slider.value = this.value;
      }

    }

    function insDistanceElement(index){
        var outerDiv = document.createElement("div");
        outerDiv.setAttribute("class","mt-4");

        var inputBar = document.createElement("input");
        inputBar.setAttribute('id',"distanceRange"+index);
        inputBar.setAttribute('name',"distance");
        inputBar.setAttribute('class',"slider");
        inputBar.setAttribute('type',"range");
        inputBar.setAttribute('min',"0");
        inputBar.setAttribute('max',"50");
        inputBar.setAttribute('step',"0.5");
        inputBar.setAttribute('value',"30");
        inputBar.setAttribute('style',"width:80%;");

        outerDiv.appendChild(inputBar);

        var innerDiv = document.createElement("div");
        innerDiv.setAttribute("class","col");
        var span = document.createElement("span");
        span.setAttribute("id","textInput"+index);
        span.innerHTML = 30+" cm";

        innerDiv.appendChild(span);
        outerDiv.appendChild(innerDiv);
        return outerDiv;

    }

    function insRow(image_url,image) {
        var x = document.getElementById('POITable').getElementsByTagName('tbody')[0];
        var len = x.rows.length;
        var new_row = x.insertRow(len);

        new_row.setAttribute('class', 'text-center');

        for (var c = 0; c < arrHead.length; c++) {
            var td = document.createElement('tr'); // tr definition.
            td = new_row.insertCell(c);
            td.setAttribute('class',"align-middle");

            if (c == 0) {
                td.appendChild(document.createTextNode(count+1));
            }


            else if (c == 1)  {
                var ele = document.createElement('img');
                ele.setAttribute('src', image_url);
                ele.setAttribute('name', "images");
                ele.setAttribute('value',image);
                ele.setAttribute('class', "img-fluid upload-image");
                ele.setAttribute('style',style="max-width:200px;max-height:200px;");
                td.appendChild(ele);
            }
            else if (c == 2) {      // the first column.
                // add a button in every new row in the first column.
                var selectList = document.createElement('select');
                var array = ["Sacral","Trochanter","Ischial","Occipital",'Heel','Ankle','Other'];

                // set input attributes.
                selectList.setAttribute('type', 'number');

                selectList.setAttribute('class', 'form-control');
                selectList.setAttribute('name', 'woundlocation');
                selectList.setAttribute('style', 'weight:100%;width: 80%;display:inline-block;');

                //Create and append the options
                for (var i = 0; i < array.length; i++) {
                    var option = document.createElement("option");
                    option.value = array[i];
                    option.text = array[i];
                    selectList.appendChild(option);
                }

                td.appendChild(selectList);
                td.appendChild(insDistanceElement(count));

            }
            else if (c == 3) {      // the first column.
                // add a button in every new row in the first column.
                var button = document.createElement('button');

                // set input attributes.
                button.setAttribute('type', 'button');
                button.setAttribute('class', 'btn btn-danger ');

                // add button's 'onclick' event.
                button.setAttribute('onclick', 'deleteRow(this)');
                button.innerHTML = '<i class="fas fa-minus"></i>';

                td.appendChild(button);
            }


        }


        count += 1;
    }
