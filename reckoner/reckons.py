from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask_login import login_required, current_user

from .__init__ import db, login_manager
from .models import User, Reckon, ReckonOption, ReckonResponse, ReckonOptionResponse, SettledReckon

bp = Blueprint('reckons', __name__, url_prefix="/reckons")

@bp.route('view')
@login_required
def view():
    # Get all reckons

    g.reckons = Reckon.query.order_by(Reckon.end_date.desc()).all()

    return render_template('reckons/view.html')

@bp.route('create', methods=('GET', 'POST'))
@login_required
def create():

    if request.method == "POST":
        question = request.form["question"]
        options = request.form["options"]
        end_date = request.form["enddate"]

        error = None 


        # Basic checks
        if question == "" or question is None:
            error = "Please enter a question."
        elif options == "" or options is None:
            error = "Please enter some options."
        elif end_date == "" or end_date is None:
            error = "Please enter an end date."
        
        if error is not None:
            print("error")
            flash({
                "message": error,
                "style": "danger"
            })

            return render_template('reckons/create.html')
        try: 
            formatted_end_date = datetime.fromisoformat(end_date)        
        except:
            flash({
                "message": "Invalid date format.",
                "style": "danger"
            })
            return render_template('reckons/create.html')

        option_list = options.split("\r\n")
        print(option_list)
        
        if error is None:
            new_reckon = Reckon(
                question = question,
                creation_date = datetime.now(),
                edit_date = datetime.now(),
                end_date = formatted_end_date,
                creator_id = current_user.id
            )
            db.session.add(new_reckon)
            db.session.commit()

            for option in option_list:
                new_option = ReckonOption(
                    option = option,
                    reckon_id = new_reckon.id
                )
                db.session.add(new_option)
            db.session.commit()

            flash({
                "message": "Reckon created successfully!",
                "style": "success"
            })
            return redirect(url_for('reckons.view'))

    return render_template('reckons/create.html')

@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):

    # Check if there are any entries - if so, lock 
    # the question and options

    # add a delete button

    reckon = Reckon.query.filter_by(id=id).first()
    #reckon_options = ReckonOption.query.filter_by(reckon_id = reckon.id).all()


    if request.method == "POST":
        # First check if anyone has made a reckon
        #existing_answers = ReckonResponse.query.filter_by()
        #if len(reckon.responses) > 0:

        question = request.form["question"]
        options = request.form["options"]
        end_date = request.form["enddate"]

        error = None 
        # Basic checks
        if question == "" or question is None:
            error = "Please enter a question."
        elif options == "" or options is None:
            error = "Please enter some options."
        elif end_date == "" or end_date is None:
            error = "Please enter an end date."
        
        if error is not None:
            print("error")
            flash({
                "message": error,
                "style": "danger"
            })

            return render_template('reckons/create.html')
        try: 
            formatted_end_date = datetime.fromisoformat(end_date)        
        except:
            flash({
                "message": "Invalid date format.",
                "style": "danger"
            })
            return render_template('reckons/create.html')

        option_list = options.split("\r\n")

        if error is None:
            # Only update the question if nobody has responded
            if len(reckon.responses) == 0:
                reckon.question = question

            # Otherwise just ipdate 
            reckon.end_date = formatted_end_date
            reckon.edit_date = datetime.now()

            db.session.add(reckon)
            db.session.commit()

            # Again only update the options if nobody has responded
            if len(reckon.responses) == 0:
                old_options = ReckonOption.query.filter_by(reckon_id=reckon.id).all()
                
                # First delete the existing ones
                for option in old_options:
                    db.session.delete(option)
                db.session.commit()

                for option in option_list:
                    new_option = ReckonOption(
                        option = option,
                        reckon_id = reckon.id
                    )
                    db.session.add(new_option)
                db.session.commit()

            flash({
                "message": "Reckon updated successfully!",
                "style": "success"
            })
            return redirect(url_for('reckons.view'))

    reckon_form = {
        "question": reckon.question,
        "options": "\r\n".join([i.option for i in reckon.options]),
        "end_date": reckon.end_date
    }

    locked = False
    if len(reckon.responses) > 0:
        locked=True

        flash({
            "message": "Reckons have already been recorded for this question, so the question and options cannot be edited.",
            "style": "info"
        })

        return render_template('reckons/edit.html', reckon=reckon_form, locked=locked)       
    
    return render_template('reckons/edit.html', reckon=reckon_form)


@bp.route('/answer/<int:id>', methods=('GET', 'POST'))
@login_required
def answer(id):

    reckon = Reckon.query.filter_by(id=id).first()

    # First check if this reckon has ended, and prevent answers if so
    if reckon.end_date < datetime.now():
        flash({
            "message": "This reckon has ended, so is not accepting any more answers. Please wait for it to be settled.",
            "style": "info"
        })
        return redirect(url_for('reckons.view'))

    last_response = ReckonResponse.query.filter_by(user_id=current_user.id).order_by(ReckonResponse.response_date.desc()).first()
    #print(last_response.response_answers)
    # Get the newest guesses so they can be loaded up
    previous_reckon_answers = None
    if last_response is not None:
        previous_reckon_answers = {}
        for response_answer in last_response.response_answers:
            name = "option{}".format(response_answer.reckon_option_id)
            previous_reckon_answers[name] = response_answer.probability

    if request.method == "POST":
        response_keys = {}
        for option in reckon.options:
            name = "option{}".format(option.id)
            response_keys[option.id] = float(request.form[name])
            if request.form[name] is None:
                response_keys[option.id] = 0.0

        if sum(response_keys.values()) != 1.0:
            flash({
                "message": "Probabilities must sum to one.",
                "style": "danger"
            })
            return render_template('reckons/answer.html', reckon=reckon)
        else:
            new_response = ReckonResponse(
                    reckon_id = reckon.id,
                    user_id = current_user.id,
                    response_date = datetime.now()
                )
            db.session.add(new_response)
            db.session.commit()

            for k,v in response_keys.items():
                new_answer_response = ReckonOptionResponse(
                    reckon_response_id = new_response.id,
                    probability = v,
                    reckon_option_id = k
                )
                db.session.add(new_answer_response)
                
            db.session.commit()
            flash({
                "message": "Your reckon has been reckoned.",
                "style": "success"
            })
            return redirect(url_for('reckons.view'))


    return render_template('reckons/answer.html', reckon=reckon, previous_reckon_answers=previous_reckon_answers)

@bp.route('/settle/<int:id>', methods=('GET', 'POST'))
@login_required
def settle(id):

    reckon = Reckon.query.filter_by(id=id).first()
    
    if reckon is None:
        flash({
            "message": "Invalid reckon ID.",
            "style": "danger"
        })
        return redirect(url_for('reckons.view'))

    # Check if it has been settled and we are updating
    settle = SettledReckon.query.filter_by(reckon_id = reckon.id).first()
    
    if request.method == "POST":
        correct_option = request.form["correct_option"]

        # Check this is a valid option
        if ReckonOption.query.filter_by(id = correct_option).first() is None:
            flash({
                "message": "Invalid option ID.",
                "style": "danger"
            })
            return redirect(url_for('reckons.settle'))
        


        if settle is None:
            # Commit a new settle
            new_settle = SettledReckon(
                reckon_id = reckon.id,
                reckon_option_id = correct_option,
                settled_date = datetime.now()
            )
            db.session.add(new_settle)
        else:
            # update the existing one
            settle.reckon_option_id = correct_option
            settle.settled_date = datetime.now()
            db.session.add(settle)
        
        db.session.commit()

        # Finally end the reckon
        reckon.ended = True
        db.session.add(reckon)
        db.session.commit()

        flash({
            "message": "Reckon settled successfully.",
            "style": "success"
        })

        return redirect(url_for('reckons.view'))


    return render_template('reckons/settle.html', reckon=reckon, settle=settle)

@bp.route('/board/<int:id>')
@login_required
def board(id):
    reckon = Reckon.query.filter_by(id=id).first()
    
    if reckon is None:
        flash({
            "message": "Invalid reckon ID.",
            "style": "danger"
        })
        return redirect(url_for('reckons.view'))

    # Get the list of users who have responded
    user_ids = set([i.user_id for i in reckon.responses])

    user_responses = []

    # Now get the newest response from each
    for user_id in user_ids:
        response = ReckonResponse.query.\
            filter_by(reckon_id = reckon.id, user_id = user_id).\
                order_by(ReckonResponse.response_date.desc()).first()
        if response is not None:
            user_responses.append(response)

    
    # Check for a settle
    settle = SettledReckon.query.filter_by(reckon_id=reckon.id).first()        

    return render_template('reckons/board.html', reckon=reckon, responses=user_responses, settle=settle)
