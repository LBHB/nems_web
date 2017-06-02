from flask import render_template, jsonify, request
from nems_analysis import app, session, NarfAnalysis, NarfBatches, NarfResults
from nems_analysis.ModelFinder import ModelFinder
from nems_analysis.PlotGenerator import Scatter_Plot, Bar_Plot, Pareto_Plot
import pandas.io.sql as psql
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc


##################################################################
####################   UI UPDATE FUNCTIONS  ######################
##################################################################


# landing page
@app.route('/')
def main_view():
    # .all() returns a list of tuples, list comprehension to pull tuple
    # elements out into list
    analysislist = [i[0] for i in session.query(NarfAnalysis.name).all()]
    batchlist = [i[0] for i in session.query(NarfAnalysis.batch).distinct().all()]
    
    ######  DEFAULT SETTINGS FOR RESULTS DISPLAY  ################
    # TODO: let user choose their defaults and save for later sessions
    defaultcols = ['id','cellid','batch','modelname','r_test','r_fit','n_parms']
    defaultrowlimit = 500
    defaultsort = 'cellid'
    ##############################################################
    
    measurelist = ['r_ceiling','r_test','r_fit','r_active','mse_test','mse_fit',\
                   'mi_test','mi_fit','nlogl_test','nlogl_fit','cohere_test',\
                   'cohere_fit']
    
    # returns all columns in the format 'NarfResults.columnName'
    # then removes the leading 'NarfResults.' from each string
    collist = ['%s'%(s) for s in NarfResults.__table__.columns]
    collist = [s.replace('NarfResults.','') for s in collist]

    return render_template('main.html',analysislist = analysislist,\
                           batchlist = batchlist, collist=collist,\
                           defaultcols = defaultcols,measurelist=measurelist,\
                           defaultrowlimit = defaultrowlimit,sortlist=collist,\
                           defaultsort=defaultsort,\
                           )
    
@app.route('/update_batch')
def update_batch():
    aSelected = request.args.get('aSelected',type=str)
    
    batch = session.query(NarfAnalysis.batch).filter\
            (NarfAnalysis.name == aSelected).first()[0]
    
    return jsonify(batch = batch)
    

@app.route('/update_models')
def update_models():
    aSelected = request.args.get('aSelected',type=str)
    
    modeltree = session.query(NarfAnalysis.modeltree).filter\
                (NarfAnalysis.name == aSelected).first()[0]
                
    mf = ModelFinder(modeltree)
    modellist = mf.modellist
    
    return jsonify(modellist=modellist)

@app.route('/update_cells')
def update_cells():
    #just use first 3 indices of str to get the integer-only representation
    bSelected = request.args.get('bSelected',type=str)[:3]

    celllist = [i[0] for i in session.query(NarfBatches.cellid).filter\
               (NarfBatches.batch == bSelected).all()]
               
    return jsonify(celllist=celllist)

@app.route('/update_results')
def update_results():

    nullselection = 'MUST SELECT A BATCH AND ONE OR MORE CELLS AND ONE OR MORE\
                    MODELS AND ONE OR MORE COLUMNS BEFORE RESULTS WILL UPDATE'
    
    bSelected = request.args.get('bSelected')
    cSelected = request.args.getlist('cSelected[]')
    mSelected = request.args.getlist('mSelected[]')
    colSelected = request.args.getlist('colSelected[]')
    if (len(bSelected) == 0) or (len(cSelected) == 0) or (len(mSelected) == 0)\
                                                    or (len(colSelected) == 0):
        return jsonify(resultstable=nullselection)
    bSelected = bSelected[:3]
    
    cols = [getattr(NarfResults,c) for c in colSelected if hasattr(NarfResults,c)]
    rowlimit = request.args.get('rowLimit',500)
    ordSelected = request.args.get('ordSelected')
    if ordSelected == 'asc':
        ordSelected = asc
    elif ordSelected == 'desc':
        ordSelected = desc
    sortSelected = request.args.get('sortSelected','cellid')


    results = psql.read_sql_query(Query(cols,session).filter\
              (NarfResults.batch == bSelected).filter\
              (NarfResults.cellid.in_(cSelected)).filter\
              (NarfResults.modelname.in_(mSelected)).order_by(ordSelected\
              (getattr(NarfResults,sortSelected))).limit(rowlimit).statement,\
              session.bind)
    
    return jsonify(resultstable=results.to_html(classes='table-hover\
                                                table-condensed'))


@app.route('/update_analysis_details')
def update_analysis_details():
    
    aSelected = request.args.get('aSelected')
    
    return jsonify(details=('testing: ' + aSelected))


####################################################################
####################    PLOT FUNCTIONS    ##########################
####################################################################


# TODO: May want to split these up into a separate 'plot' package with
#       its own folder and views file as options grow

# TODO: Is POST the correct method to use here? Couldn't get GET to work,
#       but might be a better way than HTML forms via JS etc.
@app.route('/scatter_plot', methods=['POST'])
def scatter_plot():
    
    bSelected = request.form.get('batch')[:3]
    mSelected = request.form.getlist('modelnames')
    cSelected = request.form.getlist('celllist')
    measure = request.form['measure']
    
    results = psql.read_sql_query(session.query(getattr(NarfResults,measure),NarfResults.cellid,\
              NarfResults.modelname).filter(NarfResults.batch == bSelected).filter\
              (NarfResults.cellid.in_(cSelected)).filter\
              (NarfResults.modelname.in_(mSelected)).statement,session.bind)
              
    plot = Scatter_Plot(data=results,celllist=cSelected,modelnames=mSelected,\
                        measure=measure, batch=bSelected)
    plot.generate_plot()
    
    return render_template("plot.html", script=plot.script, div=plot.div)


@app.route('/bar_plot',methods=['POST'])
def bar_plot():
    # TODO: this is exactly the same as scatter_plot other than the function call
    # to Bar_Plot instead of Scatter_Plot - should these be combined into a
    # single function or left separate for clarity?
    
    bSelected = request.form.get('batch')[:3]
    mSelected = request.form.getlist('modelnames')
    cSelected = request.form.getlist('celllist')
    measure = request.form['measure']
    
    results = psql.read_sql_query(session.query(getattr(NarfResults,measure),NarfResults.cellid,\
              NarfResults.modelname).filter(NarfResults.batch == bSelected).filter\
              (NarfResults.cellid.in_(cSelected)).filter\
              (NarfResults.modelname.in_(mSelected)).statement,session.bind)
        
    plot = Bar_Plot(data=results,celllist=cSelected,modelnames=mSelected,\
                    measure=measure,batch=bSelected)
    plot.generate_plot()
    
    return render_template("plot.html",script=plot.script,div=plot.div)


@app.route('/pareto_plot',methods=['POST'])
def pareto_plot():
    
    bSelected = request.form.get('batch')[:3]
    mSelected = request.form.getlist('modelnames')
    cSelected = request.form.getlist('celllist')
    measure = request.form['measure']
    
    results = psql.read_sql_query(session.query(getattr(NarfResults,measure),\
              NarfResults.cellid,NarfResults.n_parms,\
              NarfResults.modelname).filter(NarfResults.batch == bSelected).filter\
              (NarfResults.cellid.in_(cSelected)).filter\
              (NarfResults.modelname.in_(mSelected)).statement,session.bind)
        
    plot = Pareto_Plot(data=results,celllist=cSelected,modelnames=mSelected,\
                    measure=measure,batch=bSelected)
    plot.generate_plot()
    
    return render_template("plot.html",script=plot.script,div=plot.div)
####################################################################
###################     MISCELLANEOUS  #############################
####################################################################


# clicking error log link will open text file with notes
# TODO: add interface to edit text from site, or submit notes some other way,
# so that users can report bugs/undesired behavior
@app.route('/error_log')
def error_log():
    return app.send_static_file('error_log.txt')