import { atom, selector } from 'recoil';

export const userState = atom({
  key: 'userState',
  default: JSON.parse(localStorage.getItem('user')) || null,
});

export const tokenState = atom({
  key: 'tokenState',
  default: localStorage.getItem('token') || null,
});

export const isAuthenticatedState = selector({
  key: 'isAuthenticatedState',
  get: ({get}) => {
    const token = get(tokenState);
    const user = get(userState);
    return !!token && !!user;
  },
});
