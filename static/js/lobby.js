$("#lobby_form").submit((e) => {
    e.preventDefault()

    sessionStorage.setItem('display_name', e.target.name.value)

    let inviteCode = e.target.room.value
    if(!inviteCode){
        inviteCode = String(Math.floor(Math.random() * 10000))
    }
    window.location = `room?room=${inviteCode}`
});