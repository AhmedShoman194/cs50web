var count = 0;
document.addEventListener('DOMContentLoaded', () => {
    const num = parseInt(document.querySelector("#num").value);
    for (j = 0; j < num; j++) {
        const topText = document.querySelector(`[data-id= "${count}"]`).value;
        const topTextSize = document.querySelector(`[data-id= "${count + 1}"]`).value;
        const bottomText = document.querySelector(`[data-id= "${count + 2}"]`).value;
        const bottomTextSize = document.querySelector(`[data-id= "${count + 3}"]`).value;
        const temp = document.querySelector(`[data-id= "${count + 5}"]`).value;
        const canvas = document.getElementById(`${count + 4}`);
        count = count + 6;

        const context = canvas.getContext('2d');
        canvas.width = canvas.height = 0;

        const img = new Image;
        img.src = temp;
        img.onload = () => {generateMeme(canvas, context, img, topText, bottomText, topTextSize, bottomTextSize);};
    };
});

function generateMeme(canvas, context, img, topText, bottomText, ts, bs){
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
};

