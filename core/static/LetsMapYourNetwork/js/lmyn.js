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
        filterHTML =  '<a id="filtera" class="btn icon-btn btn-warning" href="#" onclick="removeFilter(this,'+"'"+project_id+"'"+');" style="padding: 1px 6px 3px 2px;font-size:12px;border-radius:50px;background:#3971ac;border-color:#3971ac;font-weight:700"> \
                       <i class="glyphicon glyphicon-remove" style="padding:2px 5px;color: rgb(184, 199, 206)"></i>'
                        + source.innerHTML
                        + '</a>';
        filterSpan.innerHTML += filterHTML;
        links = document.getElementById('filterSpan').getElementsByTagName('a');
        filterString = ' AND (n.action =~ ".*' + source.innerHTML + '.*"';
        for (i=0;i<links.length;i++)
        {
            filterString += ' OR n.action =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*"';
        }
        filterString += ') ';
        $('#graph-container').empty();
        updateGraph(filterString, project_id);

    }

    function removeFilter(source,project_id)
    {
        $("a").filter(".icon-btn").remove( ":contains('"+ source.innerHTML.substring(source.innerHTML.indexOf("</i>") + "</i>".length) +"')");
        links = document.getElementById('filterSpan').getElementsByTagName('a');
        if (links.length <= 0)
        {
            filterString = '';
        }
        else
        {
            filterString = ' AND (n.action =~ ".*' + links[0].innerHTML.substring(links[0].innerHTML.indexOf("</i>") + "</i>".length) + '.*"';
            for (i=0;i<links.length;i++)
            {
                filterString += ' OR n.action =~ ".*' + links[i].innerHTML.substring(links[i].innerHTML.indexOf("</i>") + "</i>".length) + '.*"';
            }
            filterString += ') ';
        }
        $('#graph-container').empty();
        updateGraph(filterString, project_id);

    }

    function updateGraph(filter, project_id)
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
                // Initialize the dragNodes plugin:
                var dragListener = sigma.plugins.dragNodes(s, s.renderers[0]);

                dragListener.bind('startdrag', function (event) {
                    console.log(event);
                });
                dragListener.bind('drag', function (event) {
                    console.log(event);
                });
                dragListener.bind('drop', function (event) {
                    console.log(event);
                });
                dragListener.bind('dragend', function (event) {
                    console.log(event);
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