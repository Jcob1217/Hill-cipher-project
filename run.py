import threading
from flask import Flask, render_template, url_for, flash, Markup
from forms import Encryption, Decryption, Guessed, BruteForce
import array_to_latex as a2l
from hill_rewrite import HillCipher, brute_force_thread


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
default_aplh = 'abcdefghijklmnopqrstuvwxyz'


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/szyfrowanie", methods=['GET', 'POST'])
def szyfrowanie():
    form = Encryption()
    if form.validate_on_submit():
        try:
            message_fixed, encryption_matrix_mutipled, message_matrix, matrix_from_key, matrix_encrypted, encrypted_message = \
                HillCipher(alphabet=form.alphabet.data).encrypt(message=form.message.data, key=form.key.data)
            matrix_from_key = a2l.to_ltx(matrix_from_key, frmt='{:6}', print_out=False)
            matrix_encrypted = a2l.to_ltx(matrix_encrypted, frmt='{:6}', print_out=False)
            message_matrix = a2l.to_ltx(message_matrix, frmt='{:6}', print_out=False)
            encryption_matrix_mutipled = a2l.to_ltx(encryption_matrix_mutipled, frmt='{:6}', print_out=False)
            flash(f'Wiadomość została zaszyfrowana.', 'success')
            if form.message.data.lower() != message_fixed:
                return render_template('szyfrowanie.html', title='About', form=form, matrix_from_key=matrix_from_key,
                                       matrix_encrypted=matrix_encrypted, message_matrix=message_matrix,
                                       message_fixed=message_fixed, encrypted_message=encrypted_message,
                                       encryption_matrix_mutipled=encryption_matrix_mutipled, modulo = len(form.alphabet.data))
            return render_template('szyfrowanie.html', title='About', form=form, matrix_from_key=matrix_from_key,
                                   matrix_encrypted=matrix_encrypted, message_matrix=message_matrix,
                                   encrypted_message=encrypted_message, encryption_matrix_mutipled=encryption_matrix_mutipled, modulo = len(form.alphabet.data))
        except Exception as e:
            flash(Markup(e), 'danger')
    form.alphabet.data = default_aplh
    return render_template('szyfrowanie.html', title='About', form=form)


@app.route("/deszyfrowanie", methods=['GET', 'POST'])
def deszyfrowanie():
    form = Decryption()
    if form.validate_on_submit():
        try:
            matrix_decryption, decryption_multiplier, matrix_from_key, inverse_key, matrix_encrypted, decrypted_message =\
                HillCipher(alphabet=form.alphabet.data)\
                    .decrypt(key=form.key.data, message_enc=form.message.data)
            matrix_from_key = a2l.to_ltx(matrix_from_key, frmt='{:6}', print_out=False)
            matrix_decryption = a2l.to_ltx(matrix_decryption, frmt='{:6}', print_out=False)
            matrix_encrypted = a2l.to_ltx(matrix_encrypted, frmt='{:6}', print_out=False)
            inverse_key = a2l.to_ltx(inverse_key, frmt='{:6}', print_out=False)
            decryption_multiplier = a2l.to_ltx(decryption_multiplier, frmt='{:6}', print_out=False)
            flash(f'Wiadomość została odszyfrowana.', 'success')
            return render_template('deszyfrowanie.html', title='About', form=form, matrix_from_key=matrix_from_key,
                                   matrix_encrypted=matrix_encrypted, matrix_decryption=matrix_decryption,
                                   decrypted_message=decrypted_message, inverse_key=inverse_key,
                                   decryption_multiplier=decryption_multiplier,  modulo = len(form.alphabet.data))
        except Exception as e:
            flash(Markup(e), 'danger')
    form.alphabet.data = default_aplh
    return render_template('deszyfrowanie.html', title='About', form=form)

@app.route("/znajac_pierwsze_slowo", methods=['GET', 'POST'])
def znajac_pierwsze_slowo():
    form = Guessed()
    if form.validate_on_submit():

        lista_rozwiazan = HillCipher().decypt_with_4_letters(form.encrypted.data, form.word.data)
        flash(f'Wiadomość została odszyfrowana', 'success')
        return render_template('znajac_pierwsze_slowo.html', title='About', form=form, lista_rozwiazan=lista_rozwiazan)
    return render_template('znajac_pierwsze_slowo.html', title='About', form=form)


@app.route("/bruteforce", methods=['GET', 'POST'])
def bruteforce():
    form = BruteForce()
    if form.validate_on_submit():
        try:
            active_bruteforces = [thread for thread in threading.enumerate() if thread.name =="BRUTEFORCE"]
            if len(active_bruteforces) <= 3:
                threading.Thread(name='BRUTEFORCE', target=brute_force_thread, args=(form.message.data, form.alphabet.data)).start()
                url = url_for('static', filename=f'bruteforce/{form.message.data}.txt', _external=True)
                message = f"<a href={url}><h1>Należy odwiedzić link {url}</h1></a>" \
                          f"<h2>Należy też odświeżać odwiedzoną stronę, gdyż wyniki są aktualizowane na bieżaco.</h2>"
                return render_template('bruteforce.html', form=form, message=Markup(message))
            else:
                flash('Aktualnie trwa już łamanie innych wiadomości, trzeba chwilę poczekać i spróbować ponownie :)', 'danger')
        except Exception as e:
            flash(Markup(e), 'danger')
    form.alphabet.data = default_aplh
    return render_template('bruteforce.html', form=form)


@app.route("/instrukcja")
def instrukcja():
    return render_template('instrukcja.html')


if __name__ == '__main__':
    app.run(debug=True)