$(document).ready(function(){       
    $("#analysisSelector").change(function(){
        alert("Analysis selection has changed!");
        // if analysis selection changes, get the value selected
        var aSelected = $("#analysisSelector").val();
                         
        // pass the value to '/update_batch' in nemsweb.py
        // get back associated batchnum and change batch selector to match
        $.ajax({
            url: $SCRIPT_ROOT + '/update_batch',
            data: { aSelected:aSelected }, 
            type: 'GET',
            success: function(data) {
                console.log("batchnum retrieved?: " + data.batchnum);
                $("select[name='batchnum']").val(data.batchnum);
            },
            error: function(error) {
                console.log(error);
            }
        });
        // also pass analysis value to 'update_models' in nemsweb.py
        $.ajax({
            url: $SCRIPT_ROOT + '/update_models',
            data: { aSelected:aSelected }, 
            type: 'GET',
            success: function(data) {
                console.log("modellist = " + data.modellist);
                var $models = $("select[name='modelnames']");
                $models.empty();
                             
                $.each(data.modellist, function(modelname) {
                    console.log("modelname = " + data.modellist[modelname]);
                    $models.append($("<option></option>")
                        .attr("value", data.modellist[modelname]).text
                        (data.modellist[modelname]));
                });
            },
            error: function(error) {
                console.log(error);
            }     
        });
    });

    $("input[name='batchnum']").change(function(){
        // TODO: update cell list when batch changes
        //       should cascade from change to analysis selection
        alert("Value of batch selection has changed!");
        // if batch selection changes, get the value of the new selection
        var bSelected = $("input[name='batchnum']:selected").val();

        $.ajax({
            url: $SCRIPT_ROOT + '/update_cells',
            data: { bSelected:bSelected },
            type: 'GET',
            success: function(newCells) {
                cells = $("select[name='celllist']");
                cells.empty();
                alert("Inside cell update function");

                $.each(newCells.celllist, function(cell) {
                    cells.append($("<option></option>")
                        .attr("value", cell).text(cell));                    
                });
            },
            error: function(error) {
                console.log(error);
            }    
        });
    });
});
        
