let topTextInput, bottomTextInput, imageInput, generateBtn, canvas, context, topSize, bottomSize;

document.addEventListener('DOMContentLoaded', () => {
    topTextInput = document.getElementById('top_text');
    bottomTextInput = document.getElementById('bottom_text');
    imageInput = document.getElementById('image_input');
    generateBtn = document.getElementById('generate_btn');
    canvas = document.getElementById('meme_canvas');
    topSize = document.getElementById('top_size');
    bottomSize = document.getElementById('bottom_size');

    context = canvas.getContext('2d');

    canvas.width = canvas.height = 0;

    generateBtn.addEventListener('click', () => {
        let reader = new FileReader();
        reader.readAsDataURL(imageInput.files[0]);
        reader.onload = () => {
            let img = new Image;
            img.src = reader.result;
            img.onload = () =>{generateMeme(img, topTextInput.value, bottomTextInput.value, topSize.value, bottomSize.value);}
            
        };
    });
    
});

function generateMeme(img, topText, bottomText, ts, bs){
    canvas.width = img.width;
    canvas.height = img.height;

    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(img, 0, 0);

    let tfs = canvas.width * ts;
    let bfs = canvas.width * bs;
    
    context.fillStyle = 'white';
    context.strokeStyle = 'black';
    context.textAlign = 'center';
    
    context.font = tfs + 'px Impact';
    context.lineWidth = tfs / 25;
    topText.split('\n').forEach(function(t, i){
        context.fillText(t, canvas.width / 2, (i+1)*0.15*canvas.height, canvas.width);
        context.strokeText(t, canvas.width / 2, (i+1)*0.15*canvas.height, canvas.width);
    });

    context.font = bfs + 'px Impact';
    context.lineWidth = bfs / 25;
    bottomText.split('\n').reverse().forEach(function(t, i){
        context.fillText(t, canvas.width / 2, canvas.height - (i+0.3)*bfs, canvas.width);
        context.strokeText(t, canvas.width / 2, canvas.height - (i+0.3)*bfs, canvas.width);
    });
}
