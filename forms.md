<!DOCTYPE html>
<html lang="en">
<head>
    <title>Two Forms with Shared Fields (Bootstrap)</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body>

<div class="container mt-3">
    <h2>Shared Fields</h2>
    <div id="shared-fields" class="mb-3">
        <div class="form-group mb-3">
            <label for="sharedField1" class="form-label">Shared Field 1:</label>
            <input type="text" class="form-control" id="sharedField1" name="sharedField1" required>
        </div>
        <div class="form-group mb-3">
            <label for="sharedField2" class="form-label">Shared Field 2:</label>
            <input type="text" class="form-control" id="sharedField2" name="sharedField2" required>
        </div>
    </div>

    <h2>Form 1</h2>
    <form id="form1" action="central_submission_url" method="post">
        <div id="form1-fields">
            <input type="hidden" name="form_type" value="form1">
            <div class="form-group mb-3">
                <label for="form1Field" class="form-label">Form 1 Specific Field:</label>
                <input type="text" class="form-control form1-required" id="form1Field" name="form1Field">
            </div>
            <button type="submit" class="btn btn-primary" name="submit_form" value="Submit Form 1">Submit Form 1</button>
        </div>
    </form>

    <h2>Form 2</h2>
    <form id="form2" action="central_submission_url" method="post">
        <div id="form2-fields">
            <input type="hidden" name="form_type" value="form2">
            <div class="form-group mb-3">
                <label for="form2Field" class="form-label">Form 2 Specific Field:</label>
                <input type="text" class="form-control form2-required" id="form2Field" name="form2Field">
            </div>
            <button type="submit" class="btn btn-primary" name="submit_form" value="Submit Form 2">Submit Form 2</button>
        </div>
    </form>
</div>

<script>
    document.querySelectorAll('#form1-fields input.form1-required').forEach(input => {
        input.removeAttribute('required');
    });
    document.querySelectorAll('#form2-fields input.form2-required').forEach(input => {
        input.removeAttribute('required');
    });

    document.querySelector('#form1-fields button[type="submit"]').addEventListener('click', function() {
        document.querySelectorAll('#form1-fields input.form1-required').forEach(input => {
            input.setAttribute('required', 'required');
        });
        document.querySelectorAll('#form2-fields input.form2-required').forEach(input => {
            input.removeAttribute('required');
        });
    });

    document.querySelector('#form2-fields button[type="submit"]').addEventListener('click', function() {
        document.querySelectorAll('#form2-fields input.form2-required').forEach(input => {
            input.setAttribute('required', 'required');
        });
        document.querySelectorAll('#form1-fields input.form1-required').forEach(input => {
            input.removeAttribute('required');
        });
    });

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();

            const formType = this.querySelector('input[name="form_type"]').value;
            if (!validateForm(formType)) {
                return;
            }

            const formData = new FormData(this);
            addSharedFieldsData(formData);
            submitFormData('central_submission_url', formData);
        });
    });


    function validateForm(formType) {
        let isValid = true;
        let formSpecificFields;
        let formTitle;

        if (formType === 'form1') {
            formSpecificFields = document.querySelectorAll('#form1-fields input.form1-required');
            formTitle = 'Form 1';
        } else if (formType === 'form2') {
            formSpecificFields = document.querySelectorAll('#form2-fields input.form2-required');
            formTitle = 'Form 2';
        } else {
            return false; // Unknown form type
        }

        formSpecificFields.forEach(element => {
            if (!element.value.trim() && element.hasAttribute('required')) {
                isValid = false;
                alert('Please fill in all required fields in ' + formTitle);
                return false;
            }
        });
        if (!isValid) return false;


        const sharedFields = document.getElementById('shared-fields').querySelectorAll('input[required]');
        sharedFields.forEach(element => {
            if (!element.value.trim()) {
                isValid = false;
                alert('Please fill in all Shared Fields.');
                return false;
            }
        });

        return isValid;
    }


    function addSharedFieldsData(formData) {
        const sharedFieldsContainer = document.getElementById('shared-fields');
        const sharedInputs = sharedFieldsContainer.querySelectorAll('input');
        sharedInputs.forEach(input => {
            formData.append(input.name, input.value);
        });
    }

    function submitFormData(url, formData) {
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                alert('Form submitted successfully to ' + url);
                // Optionally: Redirect or handle success response
            } else {
                alert('Form submission failed.');
                // Optionally: Handle error response
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Network error occurred during form submission.');
        });
    }
</script>

</body>
</html>
