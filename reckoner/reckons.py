from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask_login import login_required, current_user

from sqlalchemy import func

from .__init__ import db, login_manager
from .models import User, Reckon, ReckonOption, ReckonResponse, ReckonOptionResponse, SettledReckon, UserReckonScore

bp = Blueprint('reckons', __name__, url_prefix="/reckons")

@bp.route('/')
@login_required
def index():
    """ 
    Simple index, either putting the user to the login page or to
    view reckons
    """    
    return redirect(url_for('reckons.view'))
    

@bp.route('view', defaults={"status":"active"})
@bp.route('view/<status>')
@login_required
def view(status):
    """
    A route producing a home screen, displaying all the active reckons
    """
    if status == "ended":
        reckons = Reckon.query.\
            filter_by(ended=True).\
                order_by(Reckon.end_date.desc()).all()
        show_active = False
        current_page = "view_ended"
    # Just show active ones
    else:
        reckons = Reckon.query.\
            filter_by(ended=False).\
                order_by(Reckon.end_date.desc()).all()
    
        show_active = True
        current_page = "view_active"

    return render_template('reckons/view.html', reckons=reckons, current_page=current_page, show_active=show_active)

@bp.route('create', methods=('GET', 'POST'))
@login_required
def create():
    """
    A route to create a reckon
    """

    current_page = "create"

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
        
        # Reject the form if any basic checks fail
        if error is not None:
            print("error")
            flash({
                "message": error,
                "style": "danger"
            })

            return render_template('reckons/create.html')
        
        # Now try to convert the date, rejecting if it fails
        try: 
            formatted_end_date = datetime.fromisoformat(end_date)        
        except:
            flash({
                "message": "Invalid date format.",
                "style": "danger"
            })
            return render_template('reckons/create.html')

        # Split the options and reject if there are fewer than two
        option_list = options.split("\r\n")
        
        if len(option_list) < 2:
            flash({
                "message": "Not enough options - there must be at least 2.",
                "style": "danger"
            })
            return render_template('reckons/create.html')
        
        # Create the reckon if everything is OK
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

            # Need to create each option individually.
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

    return render_template('reckons/create.html', current_page=current_page)

@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    """
    Route to edit a reckon, handling the case where responses are already logged
    """

    # Get the reckon specified by the edit
    reckon = Reckon.query.filter_by(id=id).first()

    if reckon is None:
        flash({
            "message": "Invalid reckon ID.",
            "style": "danger"
        })
        return redirect(url_for('reckons.view'))

    # Populate a dict so we can fill in the info in the form
    reckon_form = {
        "question": reckon.question,
        "options": "\r\n".join([i.option for i in reckon.options]),
        "end_date": reckon.end_date
    }

    # Now we check if responses have been logged, and lock the relevant
    # Form elements if they have

    locked = False
    if len(reckon.responses) > 0:
        locked=True

        flash({
            "message": "Reckons have already been recorded for this question, so the question and options cannot be edited.",
            "style": "info"
        })

        return render_template('reckons/edit.html', reckon=reckon_form, locked=locked)       

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
        
        # Reject the form if there is an error
        if error is not None:
            print("error")
            flash({
                "message": error,
                "style": "danger"
            })

            return render_template('reckons/edit.html')

        # Check the date is valid, rejecting if not
        try: 
            formatted_end_date = datetime.fromisoformat(end_date)        
        except:
            flash({
                "message": "Invalid date format.",
                "style": "danger"
            })
            return render_template('reckons/edit.html')

        # Check we have enough options still
        option_list = options.split("\r\n")
        if len(option_list) < 2:
            flash({
                "message": "Not enough options - there must be at least 2.",
                "style": "danger"
            })
            return render_template('reckons/edit.html')
        
        # If everything has gone OK
        if error is None:
            # Only update the question if nobody has responded
            if len(reckon.responses) == 0:
                reckon.question = question

            # Otherwise just update the date 
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

                # Then add our new ones
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

    return render_template('reckons/edit.html', reckon=reckon_form)


@bp.route('/answer/<int:id>', methods=('GET', 'POST'))
@login_required
def answer(id):
    """
    Route to handle a user answering a reckon
    """

    # Grab the reckon
    reckon = Reckon.query.filter_by(id=id).first()

    if reckon is None:
        flash({
            "message": "Invalid reckon ID.",
            "style": "danger"
        })
        return redirect(url_for('reckons.view'))

    # First check if this reckon has ended, and prevent answers if so
    if reckon.end_date < datetime.now():
        flash({
            "message": "This reckon has ended, so is not accepting any more answers. Please wait for it to be settled.",
            "style": "info"
        })
        return redirect(url_for('reckons.view'))

    # Get the last response by the user
    last_response = ReckonResponse.query.filter_by(user_id=current_user.id).order_by(ReckonResponse.response_date.desc()).first()

    # Now we need to map this to a dict which works with the form,
    # i.e. uses the correct labels
    previous_reckon_answers = None
    if last_response is not None:
        previous_reckon_answers = {}
        for response_answer in last_response.response_answers:
            name = "option{}".format(response_answer.reckon_option_id)
            previous_reckon_answers[name] = response_answer.probability

    if request.method == "POST":

        # Extract the answers from the form by assembling the appropriate
        # names (i.e. option<option_id>)
        response_keys = {}
        for option in reckon.options:
            name = "option{}".format(option.id)
            response_keys[option.id] = float(request.form[name])
            if request.form[name] is None:
                response_keys[option.id] = 0.0

        # Check if everything adds up
        if sum(response_keys.values()) != 1.0:
            flash({
                "message": "Probabilities must sum to one.",
                "style": "danger"
            })
            return render_template('reckons/answer.html', reckon=reckon)
        else:
            # Commit the response
            new_response = ReckonResponse(
                    reckon_id = reckon.id,
                    user_id = current_user.id,
                    response_date = datetime.now()
                )
            db.session.add(new_response)
            db.session.commit()

            # Then commit each of the option responses, i.e. probabilities
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
    """
    Route to settle a reckon, only available to the creator
    """

    # Get the reckon
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

        # Then we need to go through each user and compute the Brier Score
        #last_response = ReckonResponse.query.filter_by(user_id=current_user.id).order_by(ReckonResponse.response_date.desc()).first()

        # There is a better way to do this with windows but flask-sqlalchemy
        # makes it hard
        # Grab the users who have responded
        respondents = ReckonResponse.query.filter_by(reckon_id=reckon.id).with_entities(ReckonResponse.user_id).distinct().all()
        for respondent in respondents:
            newest_response = ReckonResponse.query.\
                filter_by(reckon_id=reckon.id, user_id=respondent[0]).\
                    order_by(ReckonResponse.response_date.desc()).first()
            
            # Get the responses
            newest_answers = ReckonOptionResponse.query.\
                filter_by(reckon_response_id=newest_response.id).all()

            #Calclulate the brier score components
            correct_option_int = int(correct_option)
            sq_err = [(1-i.probability)**2 \
                if i.reckon_option_id == correct_option_int \
                else (0-i.probability)**2 \
                 for i in newest_answers]

            # Retrieve any existing scores for this reckon
            existing_user_score = UserReckonScore.query.\
                filter_by(user_id=respondent.user_id, reckon_id=reckon.id).first()
            
            if existing_user_score is None:
                db.session.add(UserReckonScore(
                    reckon_id=reckon.id,
                    user_id =respondent.user_id,
                    date = datetime.now(),
                    score = sum(sq_err)
                ))
            else: # Update the score
                existing_user_score.score = sum(sq_err)
                existing_user_score.date = datetime.now()
                db.session.add(existing_user_score)
                
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
    """
    A route for a simple leaderboard for a given reckon
    """
    
    # Get and check the reckon
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

    
    # Check for a settle, so we can highlight the winning row
    settle = SettledReckon.query.filter_by(reckon_id=reckon.id).first()        

    return render_template('reckons/board.html', reckon=reckon, responses=user_responses, settle=settle)

@bp.route('/leaderboard')
@login_required
def leaderboard():
    """
    A route to display a simple leaderboard. Sum of all scores for now.
    """

    sorted_leaderboard = None
    # Generate a row for each user
    if UserReckonScore.query.all() is not None:
        users = User.query.all()

        leaderboard_data = []

        for user in users:
            avg_score = None
            if len(user.scores) > 0:
                avg_score = sum([i.score for i in user.scores])/len(user.scores)


            leaderboard_data.append({
                "name": user.name,
                "responses": len(user.scores),
                "avg_score": avg_score if avg_score is not None else -1
            })

        sorted_leaderboard = sorted(leaderboard_data, key=lambda k: k["avg_score"])

    return render_template('reckons/leaderboard.html', leaderboard=sorted_leaderboard, current_page="leaderboard")

