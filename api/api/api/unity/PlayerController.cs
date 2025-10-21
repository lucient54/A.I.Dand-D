// unity/PlayerController.cs
using Mirror;
using UnityEngine;

public class PlayerController : NetworkBehaviour
{
    [SyncVar]
    public string PlayerId;

    // Called on the local client when the player chooses an action
    public void ChooseAction(string action)
    {
        if (isLocalPlayer)
        {
            CmdSubmitAction(action);
        }
    }

    [Command]
    public void CmdSubmitAction(string action)
    {
        // Server-side call to game manager
        ServerGameManager.Instance.HandlePlayerAction(PlayerId, action);
    }
}
