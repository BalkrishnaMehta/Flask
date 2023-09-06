from flask import Flask, render_template, redirect, url_for
from forms import CourseForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


courses_list = []


@app.route('/', methods=('GET', 'POST'))
def index():
    form = CourseForm()
    if form.validate_on_submit():
        courses_list.append({'title': form.title.data,
                             'description': form.description.data,
                             'price': form.price.data,
                             'available': form.available.data,
                             'level': form.level.data
                             })
        return redirect(url_for('courses'))
    return render_template('index.html', form=form)

@app.route('/courses/')
def courses():
    return render_template('courses.html', courses_list=courses_list)

if __name__ == "__main__":
    app.run(debug=True)