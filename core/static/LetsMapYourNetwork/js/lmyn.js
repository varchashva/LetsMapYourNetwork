console.log("Starting monitoring...");
var bgActivitiesCheckFunction = setInterval(function(){
    document.getElementById('historyprogressbar').innerHTML = "IN PROGRESS";
    var width = document.getElementById("historyprogressbar").style.width;
    width = (parseInt(width.split("%")[0]) + 10)%110;
    if (width == 0){
        width += 10;
    }
    document.getElementById("historyprogressbar").style.width = width.toString() + "%";

    links = document.getElementById('filterSpan').getElementsByTagName('a');
    if (links.length <= 0)
    {
        filterString = '';
    }
    else
    {
        filterString = ' AND (';
        for (i=0;i<links.length;i++)
        {
            if (['Windows','Linux','Router','VoIP','Switch'].indexOf(links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length)) > -1)
            {
                filterString += 'n.enum =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*" OR ';
            }
            else
            {
                filterString += 'n.action =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*" OR ';
            }
        }
        filterString = filterString.substring(0,filterString.length-4) + ') ';
    }

    $('#graph-container').empty();
    updateGraph(filterString, window.location.href.split("/")[4],0);

    $.post("task_state",{task:"project_id#".concat(window.location.href.split("/")[4])},function(status)
    {
        if (status.includes("Success"))
        {
            console.log("Stopping montoring...");
            document.getElementById('historyprogressbar').innerHTML = "ALL COMPLETED";
            document.getElementById("historyprogressbar").style.width = "100%";
            updateFilters(window.location.href.split("/")[4]);
            $('#graph-container').empty();
            updateGraph(filterString, window.location.href.split("/")[4],1);
            clearInterval(bgActivitiesCheckFunction);
        }
        else
        {
            console.log("Continue monitoring...");
        }
    });
}, 5000);

$(document).ready(function(){
  $("#searchform").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $(".dropdown-menu li").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});

$(document).ready(function(){
  $("#filterform").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $(".dropdown-menu li").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});

function applyFilter(source,project_id)
{
    knownTech = ['Windows','Linux','Router','VoIP','Switch','VPCPeer','InternetGateway','VPNGateway','InlineRouter'];
    filterHTML =  '<a id="filtera" class="btn icon-btn btn-warning" href="#" onclick="removeFilter(this,'+"'"+project_id+"'"+');" style="padding: 1px 6px 3px 2px;font-size:12px;border-radius:50px;background:#3971ac;border-color:#3971ac;font-weight:700"> \
                   <i class="glyphicon glyphicon-remove" style="padding:2px 5px;color: rgb(184, 199, 206)"></i>'
                    + source.innerHTML
                    + '</a>';
    filterSpan.innerHTML += filterHTML;
    links = document.getElementById('filterSpan').getElementsByTagName('a');
    filterString = ' AND (';
    for (i=0;i<links.length;i++)
    {
        if (knownTech.indexOf(links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length)) > -1)
        {
            filterString += 'n.enum =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*" OR ';
        }
        else if((links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length)).includes("Unknown")){
            filterString += 'n.enum = "" OR ';
        }
        else if((links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length)).includes("vpc")){
            filterString += 'n.cloud =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*" OR ';
        }
        else
        {
            filterString += 'n.action =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*" OR ';
        }
    }
    filterString = filterString.substring(0,filterString.length-4) + ') ';
    $('#graph-container').empty();
    updateGraph(filterString, project_id,1);
}

function removeFilter(source,project_id)
{
    knownTech = ['Windows','Linux','Router','VoIP','Switch','VPCPeer','InternetGateway','VPNGateway','InlineRouter'];
    $("a").filter(".icon-btn").remove( ":contains('"+ source.innerHTML.substring(source.innerHTML.indexOf("</i>") + "</i>".length) +"')");
    links = document.getElementById('filterSpan').getElementsByTagName('a');
    if (links.length <= 0)
    {
        filterString = '';
    }
    else
    {
        filterString = ' AND (';
        for (i=0;i<links.length;i++)
        {
            if (knownTech.indexOf(links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length)) > -1)
            {
                filterString += 'n.enum =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*" OR ';
            }
            else if((links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length)).includes("Unknown")){
                filterString += 'n.enum = "" OR ';
            }
            else if((links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length)).includes("vpc")){
                filterString += 'n.cloud =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*" OR ';
            }
            else{
                filterString += 'n.action =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*" OR ';
            }
        }
        filterString = filterString.substring(0,filterString.length-4) + ') ';
    }
    $('#graph-container').empty();
    updateGraph(filterString, project_id,1);

}

function updateGraph(filter, project_id, makestable)
{
    sigma.neo4j.cypher(
        {
            url: 'http://localhost:7474', user: 'neo4j', password: 'Neo4j'
        },
            'MATCH (n) WHERE n.tag =~ ".*'+ project_id +'.*" ' + filter + 'OPTIONAL MATCH (n)-[r]->(m) RETURN n,r ORDER BY n.distance, n.queue',
            {
                container: 'graph-container',
                type: 'canvas',
                settings:
                    {
                        enableEdgeHovering: false, //tester demand
                        edgeHoverSizeRatio: 2.5,
                        defaultEdgeLabelColor: "#000000",
                        drawEdgeLabels: false, //defines the visibility of edge label
                        autoRescale: ['nodePosition','edgeSize'], //drawLabels: false
                    }
            },
        function (s) {
            var dragListener = sigma.plugins.dragNodes(s, s.renderers[0]);

            if(makestable){
                console.log("Stablizing graph...")
                s.startForceAtlas2();
                window.setTimeout(function() {s.killForceAtlas2()}, 2000);
            }
            dragListener.bind('startdrag', function (event) {
            });
            dragListener.bind('drag', function (event) {
            });
            dragListener.bind('drop', function (event) {
            });
            dragListener.bind('dragend', function (event) {
            });
            s.bind('overNode clickNode', function (e) {
                e.data.node.size = e.data.node.maxNodeSize;
                s.refresh();
            });
            s.bind('outNode', function (e) {
                e.data.node.size = e.data.node.minNodeSize;
                s.refresh();
            });
        }
    );
}
function updateFilters(project_id)
{
    htmlString = '<input class="form-control" id="filterform" style="padding: 10px;margin-top: -6px;border: 0;border-radius: 0;background: #f1f1f1;" placeholder="Search..." type="text">';
    var actionList = [];
    var enumList = ["Unknown"];
    var cloudList = [];

    sigma.neo4j.getNodes(
        { url: 'http://localhost:7474', user:'neo4j', password:'Neo4j' },
        'MATCH (n) WHERE n.tag =~ ".*'+ window.location.href.split("/")[4] +'.*" OPTIONAL MATCH (n)-[r]->(m) RETURN n,r ORDER BY n.distance, n.queue',
        function(result){
            result.results[0].data.forEach(function (data){
                data.graph.nodes.forEach(function (node){
                    if (node.properties.tag.toLowerCase().includes("seed")){
                        var seedactions = node.properties.action.split("$");
                        for (i=0;i<seedactions.length;i++){
                            if (seedactions[i].includes("#")){
                               actionList.push(seedactions[i].split("#")[1].split('@')[0]);
                            }
                        }
                    }
                    else{
                       if (node.properties.enum.includes("#")){
                            enumList.push(node.properties.enum.split("#")[0]);
                       }
                       if (node.properties.cloud.length > 0){
                            cloudList.push(node.properties.cloud);
                       }

                    }
                });
            });
        actionList =  [...new Set(actionList)];
        enumList =  [...new Set(enumList)];
        cloudList = [...new Set(cloudList)];
        htmlString += '<li class="dropdown-header"><b>Filter by activities</b></li>';
        actionList.forEach(action => {
            htmlString += '<li><a href="#" onclick="return applyFilter(this,'+ "'" + project_id + "'" +');">'+action +'</a></li>';
        });
        htmlString += '<li role="presentation" class="divider"></li>';
        htmlString += '<li class="dropdown-header"><b>Filter by properties</b></li>';
        enumList.forEach(enumString => {
            htmlString += '<li><a href="#" onclick="return applyFilter(this,'+ "'" + project_id + "'" +');">'+enumString+'</a></li>';
       });
       htmlString += '<li role="presentation" class="divider"></li>';
       htmlString += '<li class="dropdown-header"><b>Filter by Cloud properties</b></li>';
       cloudList.forEach(cloudString => {
            htmlString += '<li><a href="#" onclick="return applyFilter(this,'+ "'" + project_id + "'" +');">'+cloudString+'</a></li>';
       });
       document.getElementById('filterMenu').innerHTML = htmlString;
    });
}
