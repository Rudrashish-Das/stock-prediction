const APP_ID = "edf3af1616a946cba2626bad7992bcf6"
const app_cert = "886625f69bc44051a36a4a355b9b9dd8";


let uid = sessionStorage.getItem('uid')
if(!uid){
    uid = String(Math.floor(Math.random() * 10000))
    sessionStorage.setItem('uid', uid)
}

let token = null;
let client;

let rtmClient;
let channel;

const queryString = window.location.search
const urlParams = new URLSearchParams(queryString)
let roomId = urlParams.get('room')


if(!roomId){
    roomId = 'main'
}

// token = RtcTokenBuilder.buildTokenWithUid(APP_ID, app_cert, roomId, uid, RtcRole.PUBLISHER, Math.floor(Date.now()/1000) + 3600)

let displayName = sessionStorage.getItem('display_name')
if(!displayName){
    window.location = '/'
}

let localTracks = []
let remoteUsers = {}

let localScreenTracks;
let sharingScreen = false;

let joinRoomInit = async () => {
    rtmClient = await AgoraRTM.createInstance(APP_ID)
    await rtmClient.login({uid,token})

    await rtmClient.addOrUpdateLocalUserAttributes({'name':displayName})

    channel = await rtmClient.createChannel(roomId)
    await channel.join()

    channel.on('MemberJoined', handleMemberJoined)
    channel.on('MemberLeft', handleMemberLeft)
    channel.on('ChannelMessage', handleChannelMessage)

    getMembers()
    addBotMessageToDom(`Welcome to the room ${displayName}! 👋`)

    client = AgoraRTC.createClient({mode:'rtc', codec:'vp8'})
    await client.join(APP_ID, roomId, token, uid)

    client.on('user-published', handleUserPublished)
    client.on('user-left', handleUserLeft)
}

let joinStream = async () => {
    $("#join-btn").addClass("hidden");
    document.getElementsByClassName('stream_actions')[0].style.display = 'flex'

    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks({}, {encoderConfig:{
        width:{min:640, ideal:1920, max:1920},
        height:{min:480, ideal:1080, max:1080}
    }})


    let player = `<div class="video_container local-user" id="user-container-${uid}">
                    <div class="video-player" id="user-${uid}"></div>
                 </div>`

    document.getElementById('streams_container').insertAdjacentHTML('beforeend', player)
    document.getElementById(`user-container-${uid}`).addEventListener('click', expandVideoFrame)

    localTracks[1].play(`user-${uid}`)
    await client.publish([localTracks[0], localTracks[1]])
}

let switchToCamera = async () => {
    let player = `<div class="video_container local-user" id="user-container-${uid}">
                    <div class="video-player" id="user-${uid}"></div>
                 </div>`
    displayFrame.insertAdjacentHTML('beforeend', player)

    await localTracks[0].setMuted(true)
    await localTracks[1].setMuted(true)

    $("#mic-btn").removeClass("active");
    $("#screen-btn").removeClass("active");

    localTracks[1].play(`user-${uid}`)
    await client.publish([localTracks[1]])
}

let handleUserPublished = async (user, mediaType) => {
    remoteUsers[user.uid] = user

    await client.subscribe(user, mediaType)

    let player = document.getElementById(`user-container-${user.uid}`)
    if(player === null){
        player = `<div class="video_container remote-user" id="user-container-${user.uid}">
                <div class="video-player" id="user-${user.uid}"></div>
            </div>`

        document.getElementById('streams_container').insertAdjacentHTML('beforeend', player)
        document.getElementById(`user-container-${user.uid}`).addEventListener('click', expandVideoFrame)
   
    }

    if(displayFrame.style.display){
        let videoFrame = document.getElementById(`user-container-${user.uid}`)
        videoFrame.style.height = '100px'
        videoFrame.style.width = '100px'
    }

    if(mediaType === 'video'){
        user.videoTrack.play(`user-${user.uid}`)
    }

    if(mediaType === 'audio'){
        user.audioTrack.play()
    }

}

let handleUserLeft = async (user) => {
    delete remoteUsers[user.uid]
    let item = document.getElementById(`user-container-${user.uid}`)
    if(item){
        item.remove()
    }

    if(userIdInDisplayFrame === `user-container-${user.uid}`){
        displayFrame.style.display = null
        
        let videoFrames = document.getElementsByClassName('video_container')

        for(let i = 0; videoFrames.length > i; i++){
            videoFrames[i].style.height = '300px'
            videoFrames[i].style.width = '300px'
        }
    }
}

let toggleMic = async (e) => {
    let button = e.currentTarget

    if(localTracks[0].muted){
        await localTracks[0].setMuted(false)
        button.classList.add('active')
    }else{
        await localTracks[0].setMuted(true)
        button.classList.remove('active')
    }
}

let toggleCamera = async (e) => {
    let button = e.currentTarget

    if(localTracks[1].muted){
        await localTracks[1].setMuted(false)
        button.classList.add('active')
    }else{
        await localTracks[1].setMuted(true)
        button.classList.remove('active')
    }
}

let toggleScreen = async (e) => {
    let screenButton = e.currentTarget

    if(!sharingScreen){
        
        try{
            localScreenTracks = await AgoraRTC.createScreenVideoTrack()
            
            $(`#user-container-${uid}`).remove()
            displayFrame.style.display = 'block'
            
            let player = `<div class="video_container local-user" id="user-container-${uid}">
            <div class="video-player" id="user-${uid}"></div>
            </div>`
            
            displayFrame.insertAdjacentHTML('beforeend', player)
            $(`#user-container-${uid}`).on('click', expandVideoFrame)
            
            userIdInDisplayFrame = `user-container-${uid}`
            localScreenTracks.play(`user-${uid}`)
            
            await client.unpublish([localTracks[1]])
            await client.publish([localScreenTracks])
            
            let videoFrames = document.getElementsByClassName('video_container')
            for(let i = 0; videoFrames.length > i; i++){
                if(videoFrames[i].id != userIdInDisplayFrame){
                    videoFrames[i].style.height = '100px'
                    videoFrames[i].style.width = '100px'
                }
            }

            screenButton.classList.add('active')
            $("#camera-btn").removeClass("active");
            $("#camera-btn").removeClass("hidden");

            sharingScreen = true;

        }catch(error){
            console.log(error.stack);
            sharingScreen = false;
        }
        
        
    }else{
        $("#camera-btn").removeClass("hidden");
        $(`#user-container-${uid}`).remove()
        await client.unpublish([localScreenTracks])
        
        sharingScreen = false 
        switchToCamera()
    }
}

let leaveStream = async (e) => {
    e.preventDefault()

    $("#join-btn").removeClass("hidden");
    document.getElementsByClassName('stream_actions')[0].style.display = 'none'

    for(let i = 0; localTracks.length > i; i++){
        localTracks[i].stop()
        localTracks[i].close()
    }

    await client.unpublish([localTracks[0], localTracks[1]])

    if(localScreenTracks){
        await client.unpublish([localScreenTracks])
    }

    document.getElementById(`user-container-${uid}`).remove()

    if(userIdInDisplayFrame === `user-container-${uid}`){
        displayFrame.style.display = null

        for(let i = 0; videoFrames.length > i; i++){
            videoFrames[i].style.height = '300px'
            videoFrames[i].style.width = '300px'
        }
    }

    channel.sendMessage({text:JSON.stringify({'type':'user_left', 'uid':uid})})
}



$("#camera-btn").on('click', toggleCamera);
$("#mic-btn").on('click', toggleMic);
$("#screen-btn").on('click', toggleScreen);
$("#join-btn").on('click', joinStream);
$("#leave-btn").on('click', leaveStream);


joinRoomInit()